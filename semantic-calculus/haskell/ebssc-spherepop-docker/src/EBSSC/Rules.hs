module EBSSC.Rules where
import EBSSC.Core
mergeSphere :: Sphere a -> Sphere a -> Sphere a
mergeSphere (Sphere _) s = s
