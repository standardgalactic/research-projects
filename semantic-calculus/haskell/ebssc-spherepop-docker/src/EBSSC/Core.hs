module EBSSC.Core where
data Sphere a = Sphere a deriving (Show,Eq,Functor)
popSphere :: Sphere a -> a
popSphere (Sphere x) = x
