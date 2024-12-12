
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
//import "../common/validation_functions.spec";
import "DBTasset-common.spec";



methods {
  function LiquidationLogic.HOOK_liquidation_before_validateLiquidationCall(uint256 userTotalDebt)
    internal => HOOK_liquidation_before_validateLiquidationCall_CVL(userTotalDebt);
}

function HOOK_liquidation_before_validateLiquidationCall_CVL(uint256 userTotalDebt) {
  assert userTotalDebt==0;
}



/*=====================================================================================
  Rule: liquidationCall_must_revert_if_totDebt_of_DBTasset_EQ_0
  =====================================================================================*/
rule liquidationCall_must_revert_if_totDebt_of_DBTasset_EQ_0(env e) {
  init_state();

  configuration();

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // BASIC ASSUMPTION FOR THE RULE
  //  require isVirtualAccActive(reserve.configuration.data);

  require scaledTotalSupplyCVL(_DBT_debt)==0;

  // THE FUNCTION CALL
  address user; uint256 debtToCover; bool receiveAToken;
  // TODO: prove the following basic erc20 property
  require aTokenBalanceOfCVL(_DBT_debt,user,e) <= scaledTotalSupplyCVL(_DBT_debt);
  liquidationCall@withrevert(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);

  assert lastReverted;
}



