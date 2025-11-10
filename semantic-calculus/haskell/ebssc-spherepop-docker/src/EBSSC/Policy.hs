module EBSSC.Policy where
import EBSSC.Core
applyPolicy :: Sphere a -> (a -> b) -> Sphere b
applyPolicy (Sphere a) f = Sphere (f a)
