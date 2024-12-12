
// aave imports
import "../AUX/CVLMocks/aToken.spec";
import "../AUX/CVLMocks/AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";
import "DBTasset-common.spec";


/*================================================================================================
  See the README.txt file in the solvency/ directory
  ================================================================================================*/

persistent ghost bool INSIDE_liquidationCall;
persistent ghost bool INSIDE_burnBadDebt;

persistent ghost uint256 _DBT_liqIND; persistent ghost uint256 _DBT_dbtIND;



/*================================================================================================
  Summarizations of HOOKS function 
  ================================================================================================*/
methods {
  function ReserveLogic.getNormalizedIncome_hook(uint256 ret_val, address aTokenAddress)
    internal => getNormalizedIncome_hook_CVL(ret_val, aTokenAddress);

  function ReserveLogic.getNormalizedDebt_hook(uint256 ret_val, address aTokenAddress)
    internal => getNormalizedDebt_hook_CVL(ret_val, aTokenAddress);

  function LiquidationLogic.HOOK_liquidation_after_updateState_DBT()
    internal => HOOK_liquidation_after_updateState_DBT_CVL();

  function LiquidationLogic.HOOK_liquidation_before_burnBadDebt()
    internal with (env e) => HOOK_liquidation_before_burnBadDebt_CVL(e);

  function LiquidationLogic.HOOK_liquidation_after_burnBadDebt()
    internal with (env e) => HOOK_liquidation_after_burnBadDebt_CVL(e);
}


function getNormalizedIncome_hook_CVL(uint256 ret_val, address aTokenAddress) {}

function getNormalizedDebt_hook_CVL(uint256 ret_val, address aTokenAddress) {
  assert (INSIDE_liquidationCall && !INSIDE_burnBadDebt) => aTokenAddress==_DBT_atoken;
  assert (INSIDE_liquidationCall && !INSIDE_burnBadDebt) => ret_val==_DBT_dbtIND;
}


// This is immediately after the call to updateState for the DBT token
function HOOK_liquidation_after_updateState_DBT_CVL() {
  assert currentContract._reserves[_DBT_asset].liquidityIndex == _DBT_liqIND;
  assert currentContract._reserves[_DBT_asset].variableBorrowIndex == _DBT_dbtIND;
}

function HOOK_liquidation_before_burnBadDebt_CVL(env e) {INSIDE_burnBadDebt = true;}
function HOOK_liquidation_after_burnBadDebt_CVL(env e) {INSIDE_burnBadDebt = false;}



/*=====================================================================================
  Rule: same_indexes__liquidationCall
  =====================================================================================*/
rule same_indexes__liquidationCall(env e) {
  INSIDE_liquidationCall = false;
  INSIDE_burnBadDebt = false;
  configuration();

  _DBT_liqIND = getReserveNormalizedIncome(e, _DBT_asset);
  _DBT_dbtIND = getReserveNormalizedVariableDebt(e, _DBT_asset);

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // BASIC ASSUMPTION FOR THE RULE
  require scaledTotalSupplyCVL(_DBT_debt)!=0;

  // THE FUNCTION CALL
  address user; uint256 debtToCover; bool receiveAToken;

  INSIDE_liquidationCall = true;
  liquidationCall(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);
  INSIDE_liquidationCall = false;

  uint256 __DBT_liqIND_after = getReserveNormalizedIncome(e, _DBT_asset);
  assert  __DBT_liqIND_after == _DBT_liqIND;

  uint256 __DBT_dbtIND_after = getReserveNormalizedVariableDebt(e, _DBT_asset);
  assert  __DBT_dbtIND_after == _DBT_dbtIND;
}
