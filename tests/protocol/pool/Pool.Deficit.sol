// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import 'forge-std/Test.sol';
import 'forge-std/StdStorage.sol';

import {IERC20} from '../../../src/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import {IERC20Detailed} from '../../../src/contracts/dependencies/openzeppelin/contracts/IERC20Detailed.sol';
import {IPool, DataTypes} from '../../../src/contracts/interfaces/IPool.sol';
import {Errors} from '../../../src/contracts/protocol/libraries/helpers/Errors.sol';
import {IAaveOracle} from '../../../src/contracts/interfaces/IAaveOracle.sol';
import {TestnetProcedures} from '../../utils/TestnetProcedures.sol';
import {IAccessControl} from '../../../src/contracts/dependencies/openzeppelin/contracts/IAccessControl.sol';
import {IAToken} from '../../../src/contracts/interfaces/IAToken.sol';
import {UserConfiguration} from '../../../src/contracts/protocol/libraries/configuration/UserConfiguration.sol';

contract PoolDeficitTests is TestnetProcedures {
  using stdStorage for StdStorage;
  using UserConfiguration for DataTypes.UserConfigurationMap;

  event DeficitCovered(address indexed reserve, address caller, uint256 amountDecreased);

  function setUp() public virtual {
    initTestEnvironment(false);
  }

  function test_eliminateReserveDeficit_exactDeficit(
    address coverageAdmin,
    uint120 supplyAmount
  ) public {
    _filterAddresses(coverageAdmin);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    deal(reserveToken, coverageAdmin, currentDeficit + 1);
    DataTypes.ReserveDataLegacy memory reserveData = contracts.poolProxy.getReserveData(
      reserveToken
    );

    vm.startPrank(coverageAdmin);
    // +1 to account for imprecision on supply
    deal(reserveToken, coverageAdmin, currentDeficit + 1);
    IERC20(reserveToken).approve(report.poolProxy, UINT256_MAX);
    contracts.poolProxy.supply(reserveToken, currentDeficit + 1, coverageAdmin, 0);
    DataTypes.UserConfigurationMap memory userConfigBefore = contracts
      .poolProxy
      .getUserConfiguration(coverageAdmin);
    assertEq(userConfigBefore.isUsingAsCollateral(reserveData.id), true);

    // eliminate deficit
    vm.expectEmit(address(contracts.poolProxy));
    emit DeficitCovered(reserveToken, coverageAdmin, currentDeficit);
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, currentDeficit);

    assertEq(contracts.poolProxy.getReserveDeficit(reserveToken), 0);
  }

  function test_eliminateReserveDeficit_exactUserBalance(
    address coverageAdmin,
    uint120 supplyAmount
  ) public {
    _filterAddresses(coverageAdmin);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    DataTypes.ReserveDataLegacy memory reserveData = contracts.poolProxy.getReserveData(
      reserveToken
    );

    vm.startPrank(coverageAdmin);
    deal(reserveToken, coverageAdmin, currentDeficit);
    IERC20(reserveToken).approve(report.poolProxy, UINT256_MAX);
    contracts.poolProxy.supply(reserveToken, currentDeficit / 2, coverageAdmin, 0);
    DataTypes.UserConfigurationMap memory userConfigBefore = contracts
      .poolProxy
      .getUserConfiguration(coverageAdmin);
    assertEq(userConfigBefore.isUsingAsCollateral(reserveData.id), true);

    uint256 deficitToCover = IERC20(reserveData.aTokenAddress).balanceOf(coverageAdmin);
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, deficitToCover);

    DataTypes.UserConfigurationMap memory userConfigAfter = contracts
      .poolProxy
      .getUserConfiguration(coverageAdmin);
    assertEq(userConfigAfter.isUsingAsCollateral(reserveData.id), false);
  }

  function test_eliminateReserveDeficit_surplus(
    address coverageAdmin,
    uint120 supplyAmount
  ) public {
    _filterAddresses(coverageAdmin);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    deal(reserveToken, coverageAdmin, currentDeficit + 1000);

    vm.startPrank(coverageAdmin);
    IERC20(reserveToken).approve(report.poolProxy, UINT256_MAX);
    contracts.poolProxy.supply(reserveToken, currentDeficit + 1000, coverageAdmin, 0);

    // eliminate deficit
    vm.expectEmit(address(contracts.poolProxy));
    emit DeficitCovered(reserveToken, coverageAdmin, currentDeficit);
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, currentDeficit + 1000);

    DataTypes.ReserveDataLegacy memory reserveData = contracts.poolProxy.getReserveData(
      reserveToken
    );
    DataTypes.UserConfigurationMap memory userConfig = contracts.poolProxy.getUserConfiguration(
      coverageAdmin
    );
    assertEq(userConfig.isUsingAsCollateral(reserveData.id), true);
  }

  function test_eliminateReserveDeficit_parcial(
    address coverageAdmin,
    uint120 supplyAmount,
    uint120 amountToCover
  ) public {
    _filterAddresses(coverageAdmin);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );
    amountToCover = uint120(bound(amountToCover, 1, currentDeficit));

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    deal(reserveToken, coverageAdmin, currentDeficit);

    vm.startPrank(coverageAdmin);
    IERC20(reserveToken).approve(report.poolProxy, UINT256_MAX);
    contracts.poolProxy.supply(reserveToken, currentDeficit, coverageAdmin, 0);

    // eliminate deficit
    vm.expectEmit(address(contracts.poolProxy));
    emit DeficitCovered(reserveToken, coverageAdmin, amountToCover);
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, amountToCover);
  }

  function test_reverts_eliminateReserveDeficit_has_borrows(
    address coverageAdmin,
    uint120 supplyAmount,
    uint120 cAdminBorrowAmount
  ) public {
    _filterAddresses(coverageAdmin);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );
    cAdminBorrowAmount = uint120(bound(cAdminBorrowAmount, 1, currentDeficit / 2));

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    deal(reserveToken, coverageAdmin, currentDeficit);

    vm.startPrank(coverageAdmin);
    IERC20(reserveToken).approve(report.poolProxy, UINT256_MAX);
    contracts.poolProxy.supply(reserveToken, currentDeficit, coverageAdmin, 0);
    contracts.poolProxy.borrow(reserveToken, cAdminBorrowAmount, 2, 0, coverageAdmin);

    vm.expectRevert(bytes(Errors.USER_CANNOT_HAVE_DEBT));
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, currentDeficit);
  }

  function test_reverts_eliminateReserveDeficit_invalid_caller(
    address caller,
    uint120 supplyAmount
  ) public {
    _filterAddresses(caller);
    (address reserveToken, uint256 currentDeficit) = _createReserveDeficit(
      supplyAmount,
      tokenList.usdx
    );

    vm.expectRevert(bytes(Errors.CALLER_NOT_UMBRELLA));
    vm.prank(caller);
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, currentDeficit);
  }

  function test_reverts_eliminateReserveDeficit_invalid_amount(
    address coverageAdmin,
    uint120 supplyAmount
  ) public {
    _filterAddresses(coverageAdmin);

    (address reserveToken, ) = _createReserveDeficit(supplyAmount, tokenList.usdx);

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    vm.startPrank(coverageAdmin);
    vm.expectRevert(bytes(Errors.INVALID_AMOUNT));
    contracts.poolProxy.eliminateReserveDeficit(reserveToken, 0);
  }

  function test_reverts_eliminateReserveDeficit_reserve_not_in_deficit(
    address coverageAdmin
  ) public {
    _filterAddresses(coverageAdmin);

    vm.prank(poolAdmin);
    contracts.poolAddressesProvider.setAddress(bytes32('UMBRELLA'), coverageAdmin);

    vm.startPrank(coverageAdmin);

    vm.expectRevert(bytes(Errors.RESERVE_NOT_IN_DEFICIT));
    contracts.poolProxy.eliminateReserveDeficit(tokenList.usdx, 1);
  }

  function _createReserveDeficit(
    uint120 supplyAmount,
    address borrowAsset
  ) internal returns (address, uint256) {
    vm.assume(supplyAmount != 0);
    deal(tokenList.wbtc, alice, supplyAmount);
    vm.startPrank(alice);
    IERC20(tokenList.wbtc).approve(address(contracts.poolProxy), supplyAmount);
    contracts.poolProxy.supply(tokenList.wbtc, supplyAmount, alice, 0);
    (, , uint256 availableBorrowsBase, , , ) = contracts.poolProxy.getUserAccountData(alice);
    vm.stopPrank();

    uint256 borrowAmount = (availableBorrowsBase * 10 ** IERC20Detailed(borrowAsset).decimals()) /
      contracts.aaveOracle.getAssetPrice(borrowAsset);

    // setup available amount to borrow
    deal(borrowAsset, carol, borrowAmount);
    vm.prank(carol);
    IERC20(borrowAsset).approve(address(contracts.poolProxy), borrowAmount);
    vm.prank(carol);
    contracts.poolProxy.supply(borrowAsset, borrowAmount, carol, 0);

    vm.prank(alice);
    contracts.poolProxy.borrow(borrowAsset, borrowAmount, 2, 0, alice);
    vm.stopPrank();

    vm.warp(block.timestamp + 30 days);

    stdstore
      .target(IAaveOracle(report.aaveOracle).getSourceOfAsset(tokenList.wbtc))
      .sig('_latestAnswer()')
      .checked_write(
        _calcPrice(IAaveOracle(report.aaveOracle).getAssetPrice(tokenList.wbtc), 20_00)
      );

    deal(borrowAsset, bob, borrowAmount);
    vm.prank(bob);
    IERC20(borrowAsset).approve(address(contracts.poolProxy), borrowAmount);
    vm.prank(bob);
    contracts.poolProxy.liquidationCall(tokenList.wbtc, borrowAsset, alice, borrowAmount, false);

    uint256 currentDeficit = contracts.poolProxy.getReserveDeficit(borrowAsset);

    assertGt(currentDeficit, 0);

    return (borrowAsset, currentDeficit);
  }

  function _filterAddresses(address user) internal view {
    vm.assume(user != address(0));
    vm.assume(user != report.proxyAdmin);
    vm.assume(user != report.poolAddressesProvider);
    vm.assume(user != alice);
    vm.assume(user != bob);
    vm.assume(user != carol);
    vm.assume(user != tokenList.usdx);
    vm.assume(user != tokenList.wbtc);
    vm.assume(user != tokenList.weth);
    vm.assume(user != 0xcF63D4456FCF098EF4012F6dbd2FA3a30f122D43);
  }
}
