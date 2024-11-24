// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Pool} from '../../munged/src/contracts/protocol/pool/Pool.sol';
import {IPoolAddressesProvider} from '../../munged/src/contracts/interfaces/IPoolAddressesProvider.sol';
import {PoolInstance} from '../../munged/src/contracts/instances/PoolInstance.sol';
import {DataTypes} from '../../munged/src/contracts/protocol/libraries/types/DataTypes.sol';
import {ReserveLogic} from '../../munged/src/contracts/protocol/libraries/logic/ReserveLogic.sol';
import {WadRayMath} from '../../munged/src/contracts/protocol/libraries/math/WadRayMath.sol';
import {LiquidationLogic} from '../../munged/src/contracts/protocol/libraries/logic/LiquidationLogic.sol';

import {DummyContract} from "./DummyContract.sol";


contract PoolInstanceHarness is PoolInstance {
  DummyContract DUMMY;

  constructor(IPoolAddressesProvider provider) PoolInstance(provider) {}

  function cumulateToLiquidityIndex(address asset,
                                    uint256 totalLiquidity,
                                    uint256 amount
                                   ) external returns (uint256) {
    return ReserveLogic.cumulateToLiquidityIndex(_reserves[asset], totalLiquidity, amount);
  }

  function getNormalizedIncome(address asset) external returns (uint256) {
    return ReserveLogic.getNormalizedIncome(_reserves[asset]);
  }

  function getNormalizedDebt(address asset) external returns (uint256) {
    return ReserveLogic.getNormalizedDebt(_reserves[asset]);
  }

  function havoc_all() public {
    DUMMY.havoc_all_dummy();
  }
  
  function rayMul(uint256 a, uint256 b) external returns (uint256) {
    return WadRayMath.rayMul(a,b);
  }
  
  function rayDiv(uint256 a, uint256 b) external returns (uint256) {
    return WadRayMath.rayDiv(a,b);
  }

  function getReserveDataExtended(address asset)
    external view returns (DataTypes.ReserveData memory) {
    return _reserves[asset];
  }

  function _burnBadDebt_WRP(address user) external {
    LiquidationLogic._burnBadDebt(_reserves, _reservesList, _usersConfig[user], _reservesCount, user); 
  }
}
