package com.stargen.tests;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import com.stargen.engine.simulation.WorldState;

public class WorldStateTest {
    @Test
    public void testAdjustmentsAffectR(){
        WorldState w = new WorldState(1.0f, 0.2f, 0.4f);
        float r0 = w.getR();
        w.addPhi(0.5f);
        w.addEntropy(0.1f);
        w.adjustLambda(0.1f);
        assertNotEquals(r0, w.getR(), "R should change after world adjustments");
    }
}
