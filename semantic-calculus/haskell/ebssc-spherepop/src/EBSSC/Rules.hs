
module EBSSC.Rules where
import EBSSC.Core
import Data.Text (Text)

data Rule = Rule
  { ruleName   :: Text
  , inputType  :: Modality
  , outputType :: Modality
  , cost       :: Double
  , applyF     :: Text -> Text
  }

applyRule :: Rule -> Sphere -> Either Text Sphere
applyRule r s =
  case lookup (inputType r) (content s) of
    Nothing -> Left "Missing input modality"
    Just v  ->
      let v' = applyF r v
          newC = (outputType r, v') : content s
      in Right s { content = newC, entropy = entropy s + cost r, provenance = ruleName r : provenance s }
