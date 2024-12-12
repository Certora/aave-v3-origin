
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

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
persistent ghost uint256 _COL_liqIND; persistent ghost uint256 _COL_dbtIND;




/*================================================================================================
  Summarizations
  ================================================================================================*/
methods {
  //TEMPORARY !!! we remove the following
  /*  function LiquidationLogic._burnBadDebt(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    uint256 reservesCount,
    address user
    ) internal => NONDET;*/

  function ReserveLogic.getNormalizedIncome_hook(uint256 ret_val, address aTokenAddress)
    internal => getNormalizedIncome_hook_CVL(ret_val, aTokenAddress);

  function ReserveLogic.getNormalizedDebt_hook(uint256 ret_val, address aTokenAddress)
    internal => getNormalizedDebt_hook_CVL(ret_val, aTokenAddress);

  function ReserveLogic._updateIndexes_hook(DataTypes.ReserveData storage reserve,
                                            DataTypes.ReserveCache memory reserveCache)
    internal => _updateIndexes_hook_CVL(reserveCache);
}

function getNormalizedIncome_hook_CVL(uint256 ret_val, address aTokenAddress) {
  assert INSIDE_liquidationCall && !INSIDE_burnBadDebt => aTokenAddress==_COL_atoken;
  assert INSIDE_liquidationCall && !INSIDE_burnBadDebt => ret_val==_COL_liqIND;
}

function getNormalizedDebt_hook_CVL(uint256 ret_val, address aTokenAddress) {}

function _updateIndexes_hook_CVL(DataTypes.ReserveCache reserveCache) {
  assert (!INSIDE_burnBadDebt && reserveCache.aTokenAddress == _COL_atoken) => currentContract._reserves[_COL_asset].liquidityIndex==_COL_liqIND;
  assert (!INSIDE_burnBadDebt && reserveCache.aTokenAddress == _COL_atoken) => currentContract._reserves[_COL_asset].variableBorrowIndex==_COL_dbtIND;
}



/*================================================================================================
  Summarizations of HOOKS function 
  ================================================================================================*/
methods {
  function LiquidationLogic.get_userCollateralBalance()
    internal returns(uint256) => NONDET;

  function LiquidationLogic.HOOK_burnCollateralATokens_after_updateState()
    internal => HOOK_burnCollateralATokens_after_updateState_CVL();

  function LiquidationLogic.HOOK_liquidation_before_burnBadDebt()
    internal with (env e) => HOOK_liquidation_before_burnBadDebt_CVL(e);

  function LiquidationLogic.HOOK_liquidation_after_burnBadDebt()
    internal with (env e) => HOOK_liquidation_after_burnBadDebt_CVL(e);
}

// This is immediately after the call to updateState for the COL token
function HOOK_burnCollateralATokens_after_updateState_CVL() {
  assert currentContract._reserves[_COL_asset].liquidityIndex == _COL_liqIND;
  assert currentContract._reserves[_COL_asset].variableBorrowIndex == _COL_dbtIND;
}

persistent ghost uint256 COL_liqIND_INTR1;
persistent ghost uint256 COL_dbtIND_INTR1;
function HOOK_liquidation_before_burnBadDebt_CVL(env e) {
  INSIDE_liquidationCall = false;
  
  COL_liqIND_INTR1 = getReserveNormalizedIncome(e, _COL_asset);
  assert  COL_liqIND_INTR1 == _COL_liqIND;

  COL_dbtIND_INTR1 = getReserveNormalizedVariableDebt(e, _COL_asset);
  assert  COL_dbtIND_INTR1 == _COL_dbtIND;
  
  INSIDE_burnBadDebt = true;
  INSIDE_liquidationCall = true;
}

persistent ghost uint256 COL_liqIND_INTR2;
persistent ghost uint256 COL_dbtIND_INTR2;
function HOOK_liquidation_after_burnBadDebt_CVL(env e) {
  INSIDE_burnBadDebt = false;
  INSIDE_liquidationCall = false;

  COL_liqIND_INTR2 = getReserveNormalizedIncome(e, _COL_asset);
  assert  COL_liqIND_INTR2 == COL_liqIND_INTR1;

  COL_dbtIND_INTR2 = getReserveNormalizedVariableDebt(e, _COL_asset);
  assert  COL_dbtIND_INTR2 == COL_dbtIND_INTR1;

  INSIDE_liquidationCall = true;
}



/*
function tokens_addresses_limitations_LQD(address asset, address atoken, address debt,
                                          address asset2, address atoken2, address debt2
                                         ) {
  require asset==100;  require atoken==10;  require debt==11; 
  require asset2==200; require atoken2==20; require debt2==21; 
}


function configuration() {
  init_state();

  _DBT_atoken = currentContract._reserves[_DBT_asset].aTokenAddress;
  _COL_atoken = currentContract._reserves[_COL_asset].aTokenAddress;            
  _DBT_debt = currentContract._reserves[_DBT_asset].variableDebtTokenAddress;
  _COL_debt = currentContract._reserves[_COL_asset].variableDebtTokenAddress;
  tokens_addresses_limitations_LQD(_DBT_asset, _DBT_atoken, _DBT_debt,
                                   _COL_asset, _COL_atoken, _COL_debt);

  require aTokenToUnderlying[_DBT_atoken]==_DBT_asset; require aTokenToUnderlying[_DBT_debt]==_DBT_asset;
  require aTokenToUnderlying[_COL_atoken]==_COL_asset; require aTokenToUnderlying[_COL_debt]==_COL_asset;
}
*/

/*=====================================================================================
  Rule: same_indexes__liquidationCall
  =====================================================================================*/
rule same_indexes__liquidationCall(env e) {
  INSIDE_liquidationCall = false;
  INSIDE_burnBadDebt = false;
  configuration();

  _DBT_liqIND = getReserveNormalizedIncome(e, _DBT_asset);
  _COL_liqIND = getReserveNormalizedIncome(e, _COL_asset);

  _DBT_dbtIND = getReserveNormalizedVariableDebt(e, _DBT_asset);
  _COL_dbtIND = getReserveNormalizedVariableDebt(e, _COL_asset);

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // BASIC ASSUMPTION FOR THE RULE
  require scaledTotalSupplyCVL(_DBT_debt)!=0; // We prove that if ==0 then the call to
                                              // liquidationCall reverts (see DBTasset-totSUP0.spec)
  require scaledTotalSupplyCVL(_COL_debt)!=0; // We treat the case where ==0 in the files COLasset-totSUP0...

  // THE FUNCTION CALL
  address user; uint256 debtToCover;
  bool receiveAToken = true;

  INSIDE_liquidationCall = true;
  liquidationCall(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);
  INSIDE_liquidationCall = false;

  uint256 __COL_liqIND_after = getReserveNormalizedIncome(e, _COL_asset);
  assert  __COL_liqIND_after == _COL_liqIND;

  uint256 __COL_dbtIND_after = getReserveNormalizedVariableDebt(e, _COL_asset);
  assert  __COL_dbtIND_after == _COL_dbtIND;
}


