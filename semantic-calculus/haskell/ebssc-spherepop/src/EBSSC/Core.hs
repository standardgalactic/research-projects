
{-# LANGUAGE DeriveGeneric #-}
module EBSSC.Core where

import GHC.Generics (Generic)
import Data.Hashable
import Data.Text (Text)

data Modality = TextM | ProofM | AudioM deriving (Eq, Ord, Show, Generic)
instance Hashable Modality

type Entropy = Double

data Sphere = Sphere
  { sphereId   :: Text
  , content    :: [(Modality, Text)]
  , entropy    :: Entropy
  , provenance :: [Text]
  } deriving (Show, Generic)

emptySphere :: Text -> Sphere
emptySphere sid = Sphere sid [] 0 []
