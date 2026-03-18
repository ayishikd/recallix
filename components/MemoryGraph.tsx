"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Sphere, Line, Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";

export type AnimationPhase = 1 | 2 | 3 | 4 | 5;

function MemoryNode({ position, color, isActive, phase }: { position: [number, number, number], color: string, isActive: boolean, phase: AnimationPhase }) {
    const meshRef = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        if (!meshRef.current) return;
        const t = state.clock.getElapsedTime();
        // Increase intensity if active or in later phases
        const intensity = (isActive || phase >= 3) ? 2 + Math.sin(t * 2) * 0.5 : 0.5;
        (meshRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = intensity;
    });

    return (
        <Float speed={isActive ? 2 : 1.5} rotationIntensity={1} floatIntensity={1}>
            <Sphere args={[isActive ? 0.12 : 0.08, 16, 16]} position={position} ref={meshRef}>
                <meshStandardMaterial
                    color={color}
                    emissive={color}
                    toneMapped={false}
                />
            </Sphere>
        </Float>
    );
}

function Connections({ nodes, phase }: { nodes: [number, number, number][], phase: AnimationPhase }) {
    // Phase 1-2: Very few or no connections
    // Phase 3-5: Dense connections
    const lineOpacity = phase <= 2 ? 0.02 : phase === 3 ? 0.2 : 0.4;

    const lines = useMemo(() => {
        const temp = [];
        const connectionProbability = phase <= 2 ? 0.05 : 0.4;
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                if (Math.random() < connectionProbability) {
                    temp.push([nodes[i], nodes[j]]);
                }
            }
        }
        return temp;
    }, [nodes, phase]);

    return (
        <group>
            {lines.map((line, idx) => (
                <Line
                    key={`${idx}-${phase}`}
                    points={[line[0], line[1]]}
                    color={phase >= 3 ? "#22d3ee" : "#3f3f46"}
                    lineWidth={phase >= 4 ? 1 : 0.5}
                    transparent
                    opacity={lineOpacity}
                />
            ))}
        </group>
    );
}

function ParticleBackground({ phase }: { phase: AnimationPhase }) {
    const points = useMemo(() => {
        const positions = new Float32Array(500 * 3);
        for (let i = 0; i < 500; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 15;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 15;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 15;
        }
        return positions;
    }, []);

    return (
        <Points positions={points} stride={3}>
            <PointMaterial
                transparent
                color={phase >= 3 ? "#22d3ee" : "#a78bfa"}
                size={phase >= 3 ? 0.03 : 0.02}
                sizeAttenuation={true}
                depthWrite={false}
                opacity={phase >= 3 ? 0.6 : 0.3}
            />
        </Points>
    );
}

export default function MemoryGraph({ phase = 1 }: { phase?: AnimationPhase }) {
    const nodes = useMemo(() => {
        const temp: [number, number, number][] = [];
        for (let i = 0; i < 24; i++) {
            temp.push([
                (Math.random() - 0.5) * 8,
                (Math.random() - 0.5) * 5,
                (Math.random() - 0.5) * 4,
            ]);
        }
        return temp;
    }, []);

    return (
        <div className="absolute inset-0 -z-10 bg-black transition-colors duration-1000">
            <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
                <ambientLight intensity={phase >= 3 ? 0.8 : 0.3} />
                <pointLight position={[10, 10, 10]} intensity={phase >= 3 ? 2 : 1} />
                <group>
                    {nodes.map((pos, idx) => (
                        <MemoryNode
                            key={idx}
                            position={pos}
                            phase={phase}
                            isActive={phase >= 3 && idx % 3 === 0}
                            color={phase <= 2 ? "#3f3f46" : idx % 2 === 0 ? "#22d3ee" : "#a78bfa"}
                        />
                    ))}
                    <Connections nodes={nodes} phase={phase} />
                    <ParticleBackground phase={phase} />
                </group>
            </Canvas>
            <div className={`absolute inset-0 bg-radial-gradient from-transparent via-black/80 to-black transition-opacity duration-1000 ${phase >= 5 ? 'opacity-80' : 'opacity-40'}`} />
        </div>
    );
}
