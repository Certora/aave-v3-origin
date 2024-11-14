import "../ERC20/erc20cvl.spec";
import "../ERC20/WETHcvl.spec";
import "../ERC721/erc721.spec";
import "../ERC1967/erc1967.spec";
import "../PriceAggregators/chainlink.spec";
import "../PriceAggregators/tellor.spec";

// aave imports
import "../Aave/aToken.spec";
import "../Aave/AddressProvider.spec";
import "../Aave/PriceOracleSentinel.spec";
import "../Aave/PriceOracle.spec";
import "../Aave/ACLManager.spec";
import "../Aave/ReserveInterestRateStrategy.spec";
import "../Aave/FlashLoanReceiver.spec";

import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";

rule check_builtin_assertions(method f)
    filtered { f -> f.contract == currentContract }
{
    env e;
    calldataarg arg;
    f(e, arg);
    assert true;
}
