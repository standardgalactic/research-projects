module Main where
import EBSSC.Core
import EBSSC.Rules
import EBSSC.Policy
main :: IO ()
main = do
  let s1 = Sphere 1
  let s2 = Sphere 2
  print $ mergeSphere s1 s2
  print $ applyPolicy s1 (+1)
