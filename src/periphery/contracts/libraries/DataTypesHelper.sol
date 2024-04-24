// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {IERC20} from 'aave-v3-core/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import {DataTypes} from 'aave-v3-core/contracts/protocol/libraries/types/DataTypes.sol';

/**
 * @title DataTypesHelper
 * @author Aave
 * @dev Helper library to track user current debt balance, used by WrappedTokenGatewayV3
 */
library DataTypesHelper {
  /**
   * @notice Fetches the user current variable debt balances
   * @param user The user address
   * @param reserve The reserve data object
   * @return The variable debt balance
   **/
  function getUserCurrentDebt(
    address user,
    DataTypes.ReserveDataLegacy memory reserve
  ) internal view returns (uint256) {
    return IERC20(reserve.variableDebtTokenAddress).balanceOf(user);
  }
}
