

methods {
  function _.ADDRESSES_PROVIDER() external => NONDET; // expect address

  function getReserveDataExtended(address) external returns (DataTypes.ReserveData memory) envfree;
  function getReserveAddressById(uint16 id) external returns (address) envfree;
  function getReservesList() external returns (address[]) envfree;
    
  function rayMul(uint256,uint256) external returns (uint256) envfree;
  function rayDiv(uint256,uint256) external returns (uint256) envfree;
}




function isVirtualAccActive(uint256 data) returns bool {
    uint mask = 0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
    return (data & ~mask) != 0;
}

function init_state() {
    // based on aTokensAreNotUnderlyings
    require forall address a. 
        a == 0 // nothing-token
        || aTokenToUnderlying[a] == 0 // underlying
        || aTokenToUnderlying[aTokenToUnderlying[a]] == 0 // aTokens map to underlyings which map to 0
    ;
    // aTokens have the AToken sort, VariableDebtTokens have the VariableDebt sort, etc...
    require forall address a. tokenToSort[currentContract._reserves[a].aTokenAddress] == AToken_token();
    require forall address a. tokenToSort[currentContract._reserves[a].variableDebtTokenAddress] == VariableDebtToken_token();
}

function tokens_addresses_limitations(address atoken, address variable, address asset) {
  require atoken==10; require variable==11; require asset==100;
  //  require weth!=10 && weth!=11 && weth!=12;

  /*  require asset != 0;
  require atoken != variable && atoken != asset;
  require variable != asset;*/
  //  require weth != atoken && weth != variable && atoken != stb;

  // The asset that current rule deals with. It is used in summarization CVL-functions,
  // see for example _accrueToTreasuryCVL().
  ASSET = asset;
}

