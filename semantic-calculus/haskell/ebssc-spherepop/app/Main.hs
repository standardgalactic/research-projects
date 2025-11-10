
module Main where
import EBSSC.Core
import EBSSC.Rules
import EBSSC.Policy
import Data.Text (pack)

demoRule :: Rule
demoRule = Rule
  { ruleName = pack "echo"
  , inputType = TextM
  , outputType = ProofM
  , cost = 0.05
  , applyF = \x -> "PROOF(" <> x <> ")"
  }

main :: IO ()
main = do
  let s0 = emptySphere (pack "s1")
      s1 = s0 { content = [(TextM, "A implies A")]}
  print $ pop demoRule s1
