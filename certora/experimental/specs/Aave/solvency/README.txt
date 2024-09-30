
The property that we prove in this directory is the following solvency invariant (for an arbitrary asset):
              (*)  Atoken.totalSupply() <= VariableDebtToken.totalSupply() + virtual_balance

Intuitively, the left hand side is the amount the the pool owes to its users, and the right hand 
side is the amount it has (either in hands - the virtual_balance, or what people owe to it - 
the VariableDebtToken.totalSupply()) (*) should be proved for the following case:
1. A function call: for example supply, withdraw, borrow, repay, repayWithATokens ...
2. Time passing (without any function being called). This is relevant because the indexes increase 
   with the time, hence the amounts that appear in (*)

Note that:
1. The above isn't a real invariant. It can be violated due to rounding errors. What we really prove
   is that the left-hand-side minus right-hand-side of (*) can't increase by more than the index 
   (in RAY units) after each function call. (it is either the liquidity-index or the variableBorrow-index
   depending on the specific function call.

2. The above is proved under the following assumptions:
   a. The pool uses virtual accounting for the asset.
   b. The asset uses only variable-debt interest (and not stable-debt). Moreover we assume that 
      StableDebtToken.totalSupply()==0. (Aave is going in that direction.)
   c. RAY <= liquidity-index  &&  RAY <= borrow-index. (this should be easy to prove)
   d. Atoken.totalSupply() <= RAY. If this assumption is removed, we either get a timeout or an error. 
      (I suspect that the error is due to an imprecision RAY-calculation with such big numbers,  but 
      haven't checked it yet.)
      
3. We deal with each function in a seperate file. For some functions (repay, repayWithATokens) we
   dedicate a sub-directory, because the proof is more involved and contains lemmas or case splits.


   
