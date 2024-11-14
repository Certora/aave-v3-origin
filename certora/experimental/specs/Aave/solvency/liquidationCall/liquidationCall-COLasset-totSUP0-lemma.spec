
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";


/*================================================================================================
  See the README.txt file in the solvency/ directory
  ================================================================================================*/

methods {
  function ReserveLogic.getNormalizedIncome_hook(uint256 ret_val, address aTokenAddress)
    internal => getNormalizedIncome_hook_CVL(ret_val, aTokenAddress);

  //  function ReserveLogic.getNormalizedDebt_hook(uint256 ret_val, address aTokenAddress)
  //  internal => getNormalizedDebt_hook_CVL(ret_val, aTokenAddress);

  //function ReserveLogic._updateIndexes_hook(DataTypes.ReserveData storage reserve,
  //                                          DataTypes.ReserveCache memory reserveCache)
  //  internal => _updateIndexes_hook_CVL(reserveCache);
  
  //  function LiquidationLogic.HOOK_liquidation_after_updateState_DBT()
  //  internal => HOOK_liquidation_after_updateState_DBT_CVL();

  function LiquidationLogic.HOOK_liquidation_after_updateState_COL()
    internal => HOOK_liquidation_after_updateState_COL_CVL();


  function IsolationModeLogic.updateIsolatedDebtIfIsolated(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ReserveCache memory reserveCache,
    uint256 repayAmount
  ) internal => updateIsolatedDebtIfIsolatedCVL();

  function LiquidationLogic._calculateAvailableCollateralToLiquidate(
    DataTypes.ReserveConfigurationMap memory collateralReserveConfiguration,
    uint256 collateralAssetPrice,
    uint256 collateralAssetUnit,
    uint256 debtAssetPrice,
    uint256 debtAssetUnit,
    uint256 debtToCover,
    uint256 userCollateralBalance,
    uint256 liquidationBonus
  ) internal returns (uint256,uint256,uint256,uint256) =>
    _calculateAvailableCollateralToLiquidateCVL();
}

function getNormalizedIncome_hook_CVL(uint256 ret_val, address aTokenAddress) {
  assert INSIDE_liquidationCall => aTokenAddress==_COL_atoken;
  assert INSIDE_liquidationCall => ret_val==_COL_liqIND;
}

function getNormalizedDebt_hook_CVL(uint256 ret_val, address aTokenAddress) {
  assert INSIDE_liquidationCall => aTokenAddress!=_COL_atoken;

  //  assert INSIDE_liquidationCall => aTokenAddress==_DBT_atoken;
  //assert INSIDE_liquidationCall => ret_val==_DBT_dbtIND;
}

function _updateIndexes_hook_CVL(DataTypes.ReserveCache reserveCache) {
  //assert reserveCache.aTokenAddress == _DBT_atoken => currentContract._reserves[_DBT_asset].liquidityIndex==_DBT_liqIND;
  //assert reserveCache.aTokenAddress == _DBT_atoken => currentContract._reserves[_DBT_asset].variableBorrowIndex==_DBT_dbtIND;

  assert reserveCache.aTokenAddress == _COL_atoken => currentContract._reserves[_COL_asset].liquidityIndex==_COL_liqIND;
  //  assert reserveCache.aTokenAddress == _COL_atoken => currentContract._reserves[_COL_asset].variableBorrowIndex==_COL_dbtIND;
}

// This is immediately after the call to updateState for the DBT token
//function HOOK_liquidation_after_updateState_DBT_CVL() {
//  assert currentContract._reserves[_DBT_asset].liquidityIndex == _DBT_liqIND;
//  assert currentContract._reserves[_DBT_asset].variableBorrowIndex == _DBT_dbtIND;
//}

// This is immediately after the call to updateState for the COL token
function HOOK_liquidation_after_updateState_COL_CVL() {
  assert currentContract._reserves[_COL_asset].liquidityIndex == _COL_liqIND;
  //  assert currentContract._reserves[_COL_asset].variableBorrowIndex == _COL_dbtIND;
}


persistent ghost bool INSIDE_liquidationCall;

persistent ghost address _DBT_asset; persistent ghost address _DBT_atoken; persistent ghost address _DBT_debt;
persistent ghost uint256 _DBT_liqIND; persistent ghost uint256 _DBT_dbtIND;

persistent ghost address _COL_asset; persistent ghost address _COL_atoken; persistent ghost address _COL_debt;
persistent ghost uint256 _COL_liqIND; persistent ghost uint256 _COL_dbtIND;


function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256,uint256) {
  uint256 a; uint256 b; uint256 c; uint256 d; // require c==0;
  return (a,b,c,d);
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  address asset;
  havoc currentContract._reserves[asset].isolationModeTotalDebt;
}


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



/*=====================================================================================
  Rule: same_indexes__liquidationCall
  =====================================================================================*/
rule same_indexes__liquidationCall(env e) {
  INSIDE_liquidationCall = false;
  configuration();

  _DBT_liqIND = getReserveNormalizedIncome(e, _DBT_asset);
  _COL_liqIND = getReserveNormalizedIncome(e, _COL_asset);

  _DBT_dbtIND = getReserveNormalizedVariableDebt(e, _DBT_asset);
  _COL_dbtIND = getReserveNormalizedVariableDebt(e, _COL_asset);

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // BASIC ASSUMPTION FOR THE RULE
  require scaledTotalSupplyCVL(_DBT_debt)!=0;
  //require scaledTotalSupplyCVL(_COL_debt)!=0;

  // THE FUNCTION CALL
  address user; uint256 debtToCover; bool receiveAToken;

  INSIDE_liquidationCall = true;
  liquidationCall(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);
  INSIDE_liquidationCall = false;

  uint256 __COL_liqIND_after = getReserveNormalizedIncome(e, _COL_asset);
  assert  __COL_liqIND_after == _COL_liqIND;

  //  uint256 __COL_dbtIND_after = getReserveNormalizedVariableDebt(e, _COL_asset);
  //assert  __COL_dbtIND_after == _COL_dbtIND;
}


