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
import "../Aave/Pool.spec";

// standard
import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";

import "../generic.spec"; // pick additional rules from here

use builtin rule sanity filtered { f -> f.contract == currentContract }

// Simple rule - depends on better summaries for `IReserveInterestRateStrategy` OR linking it (with the risk of longer running time)
// See in https://prover.certora.com/output/60724/b7043622211340e98e602bd4e46c9aff/?anonymousKey=ff16ebf727d2aa6631a187c862a845a624bf64a5
// by filtering for `virtualUnderlyingBalance` accesses in the trace
rule user_withdraw_cannot_surpass_VA() {
  env e;
  uint256 amount;
  address to;
  address asset;
  uint128 virtual_bal_before = getReserveDataExtended(e,asset).virtualUnderlyingBalance;
  withdraw(e,asset, amount, to);
  assert amount <= assert_uint256(virtual_bal_before);
}
