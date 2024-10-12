
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
  function getReserveDataExtended(address) external returns (DataTypes.ReserveData memory) envfree;

  function ReserveLogic.getNormalizedIncome(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => getNormalizedIncome_CVL();

  function ReserveLogic.getNormalizedDebt(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => _DBT_dbtIND;

  function ReserveLogic._updateIndexes_hook(DataTypes.ReserveData storage reserve,
                                            DataTypes.ReserveCache memory reserveCache)
    internal => _updateIndexes_hook_CVL(reserveCache);

  function IsolationModeLogic.updateIsolatedDebtIfIsolated(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ReserveCache memory reserveCache,
    uint256 repayAmount
  ) internal => updateIsolatedDebtIfIsolatedCVL();

  function LiquidationLogic._calculateAvailableCollateralToLiquidate(
      DataTypes.ReserveData storage,
      DataTypes.ReserveCache memory,
      address,
      address,
      uint256,
      uint256,
      uint256,
      address // IPriceOracleGetter
  ) internal returns (uint256,uint256,uint256) =>
    _calculateAvailableCollateralToLiquidateCVL();
    /* difficulty 90 */
}

function getNormalizedIncome_CVL() returns uint256 {
  uint256 col_index;
  if (INSIDE_liquidationCall)
    return col_index;
  else
    return _DBT_liqIND;
}

function _updateIndexes_hook_CVL(DataTypes.ReserveCache reserveCache) {
  require reserveCache.aTokenAddress == _DBT_atoken => currentContract._reserves[_DBT_asset].liquidityIndex==_DBT_liqIND;
  require reserveCache.aTokenAddress == _DBT_atoken => currentContract._reserves[_DBT_asset].variableBorrowIndex==_DBT_dbtIND;

  require reserveCache.aTokenAddress == _COL_atoken => currentContract._reserves[_COL_asset].liquidityIndex==_COL_liqIND;
  require reserveCache.aTokenAddress == _COL_atoken => currentContract._reserves[_COL_asset].variableBorrowIndex==_COL_dbtIND;
}

function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256) {
  uint256 a; uint256 b; uint256 c;  require c==0;
  return (a,b,c);
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  address asset;
  havoc currentContract._reserves[asset].isolationModeTotalDebt;
}


persistent ghost bool INSIDE_liquidationCall;

persistent ghost address _DBT_asset; persistent ghost address _DBT_atoken; persistent ghost address _DBT_debt;
persistent ghost uint256 _DBT_liqIND {axiom _DBT_liqIND >= 10^27;}
persistent ghost uint256 _DBT_dbtIND {axiom _DBT_dbtIND >= 10^27;}

persistent ghost address _COL_asset; persistent ghost address _COL_atoken; persistent ghost address _COL_debt;
persistent ghost uint256 _COL_liqIND; persistent ghost uint256 _COL_dbtIND;



function tokens_addresses_limitations_LQD(address asset, address atoken, address debt,
                                          address asset2, address atoken2, address debt2
                                         ) {
  require asset==100;  require atoken==10;  require debt==11; 
  require asset2==200; require atoken2==20; require debt2==21; 
  //  require weth!=10 && weth!=11 && weth!=12;

  /*  require asset != 0;
  require atoken != debt && atoken != asset;
  require debt != asset;*/
  //  require weth != atoken && weth != debt && atoken != stb;

  // The asset that current rule deals with. It is used in summarization CVL-functions,
  // see for example _accrueToTreasuryCVL().
  //  ASSET = asset;
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
  Rule: solvency__liquidationCall
  =====================================================================================*/
rule solvency__liquidationCall_DBTasset(env e) {
  INSIDE_liquidationCall = false;
  configuration();

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_DBT_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_DBT_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_DBT_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  bool exists_debt = scaledTotalSupplyCVL(_DBT_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  address user; uint256 debtToCover; bool receiveAToken;
  //  require receiveAToken==true;
  require _COL_asset != _DBT_asset;

  INSIDE_liquidationCall = true;
  liquidationCall(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);
  INSIDE_liquidationCall = false;
  
  DataTypes.ReserveData reserve2 = getReserveDataExtended(_DBT_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  require assert_uint256(reserve2.liquidityIndex) == _DBT_liqIND;
  require assert_uint256(reserve2.variableBorrowIndex) == _DBT_dbtIND;
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_DBT_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_DBT_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_DBT_asset).virtualUnderlyingBalance;

  assert __totSUP_aToken__ == __totSUP_aToken;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + CONST
    + reserve2.variableBorrowIndex / RAY()
    //    + _DBT_dbtIND / RAY()
    ;
}

