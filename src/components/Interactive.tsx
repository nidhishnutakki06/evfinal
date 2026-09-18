import React, { useRef } from 'react'
import * as THREE from 'three'
import { useHelper } from '@react-three/drei'
import { useSelection, SelectionState, type EntityType } from '../state/SelectionStore'

interface InteractiveProps {
  id: string
  type: EntityType
  children: React.ReactNode
  position?: [number, number, number]
  rotation?: [number, number, number]
}

export function Interactive({ id, type, children, position, rotation }: InteractiveProps) {
  const ref = useRef<THREE.Group>(null)
  const selection = useSelection()
  const isSelected = selection.id === id && selection.type === type

  // BoxHelper draws a clear bounding box around the entire group when selected
  useHelper(isSelected ? (ref as any) : null, THREE.BoxHelper, '#00ffff')

  const handleClick = (e: any) => {
    e.stopPropagation() // Prevent click from bubbling up or clearing selection
    SelectionState.select(type, id)
  }

  return (
    <group
      ref={ref}
      position={position}
      rotation={rotation}
      onClick={handleClick}
      onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'pointer' }}
      onPointerOut={(e) => { e.stopPropagation(); document.body.style.cursor = 'auto' }}
    >
      {children}
    </group>
  )
}
