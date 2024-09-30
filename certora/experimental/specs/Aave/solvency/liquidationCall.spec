import "../../ERC20/WETHcvl.spec";
import "../../ERC721/erc721.spec";
import "../../ERC1967/erc1967.spec";
import "../../PriceAggregators/chainlink.spec";
import "../../PriceAggregators/tellor.spec";

// aave imports
import "../aToken.spec";
import "../AddressProvider.spec";
import "../PriceOracleSentinel.spec";
import "../PriceOracle.spec";
import "../ACLManager.spec";
import "../FlashLoanReceiver.spec";

import "../../problems.spec";
import "../../unresolved.spec";

import "common/optimizations.spec";
import "common/functions.spec";
import "common/validation_functions.spec";

import "../../generic.spec"; // pick additional rules from here





/*=====================================================================================
  Rule: solvency__liquidationCall
  =====================================================================================*/
rule solvency__liquidationCall(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_stb,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset; require aTokenToUnderlying[_stb]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require scaledTotalSupplyCVL(_stb)==0;
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  // THE FUNCTION CALL
  address receiverAddress; uint256 _amount; bytes params; uint16 referralCode; 
  address collateralAsset; address user; uint256 debtToCover; bool receiveAToken;
  liquidationCall(e, collateralAsset, _asset, user, debtToCover, receiveAToken);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  //assert reserve2.liquidityIndex == assert_uint128(__liqInd_before);
  assert __totSUP_debt != 0 => (reserve2.variableBorrowIndex == assert_uint128(__dbtInd_before));
  //assert getReserveNormalizedIncome(e, _asset) == __liqInd_before;
  assert __totSUP_debt != 0 => (getReserveNormalizedVariableDebt(e, _asset) == __dbtInd_before);
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + CONST;
}

