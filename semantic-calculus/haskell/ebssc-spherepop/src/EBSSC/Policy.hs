
module EBSSC.Policy where
import EBSSC.Core
import EBSSC.Rules
import Data.Text (Text)

pop :: Rule -> Sphere -> Either Text Sphere
pop = applyRule
