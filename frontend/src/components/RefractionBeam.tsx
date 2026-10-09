// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useId } from 'react'

interface RefractionBeamProps {
  /** True while a scan runs: a light travels along the incoming ray. */
  active?: boolean
}

// Geometry in a 1200x240 box. The prism (the logo) sits at the centre; the
// fan leaves from its right face and the CSS keyframes in index.css animate
// around the same origin.
const ORIGIN = { x: 626, y: 118 }
const RAY_IN = 'M0 140 L574 119'
const END_X = 1200

/**
 * The brand signature: a warm ray (the logo's own orange) enters the prism
 * and leaves as the cool spectrum of the palette. Decorative only.
 */
export function RefractionBeam({ active = false }: RefractionBeamProps) {
  const uid = useId().replace(/:/g, '')
  const id = (name: string) => `${name}-${uid}`

  const fan = [
    { y: 40, color: 'var(--color-cyan-400)' },
    { y: 92, color: 'var(--color-primary-400)' },
    { y: 150, color: 'var(--color-secondary-400)' },
    { y: 204, color: 'var(--color-accent-400)' },
  ]

  return (
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 1200 240"
      preserveAspectRatio="xMidYMid slice"
      data-active={active}
      className="refraction pointer-events-none absolute left-0 top-1/2 h-60 w-full -translate-y-1/2"
    >
      <defs>
        <linearGradient id={id('in')} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="574" y2="0">
          <stop offset="0" style={{ stopColor: 'var(--color-warning-500)', stopOpacity: 0 }} />
          <stop offset="0.55" style={{ stopColor: 'var(--color-warning-500)', stopOpacity: 0.85 }} />
          <stop offset="1" style={{ stopColor: 'var(--color-warning-100)', stopOpacity: 1 }} />
        </linearGradient>

        <linearGradient id={id('cone')} x1="0" y1="0" x2="0" y2="1">
          {fan.map((ray, index) => (
            <stop key={ray.y} offset={index / (fan.length - 1)} style={{ stopColor: ray.color }} />
          ))}
        </linearGradient>

        <linearGradient id={id('fade')} gradientUnits="userSpaceOnUse" x1={ORIGIN.x} y1="0" x2={END_X} y2="0">
          <stop offset="0" stopColor="#fff" stopOpacity="1" />
          <stop offset="0.7" stopColor="#fff" stopOpacity="0.25" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>

        <mask id={id('mask')} maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="240">
          <rect width="1200" height="240" fill={`url(#${id('fade')})`} />
        </mask>

        {fan.map((ray) => (
          <linearGradient
            key={ray.y}
            id={id(`ray-${ray.y}`)}
            gradientUnits="userSpaceOnUse"
            x1={ORIGIN.x}
            y1={ORIGIN.y}
            x2={END_X}
            y2={ray.y}
          >
            <stop offset="0" style={{ stopColor: ray.color, stopOpacity: 0.95 }} />
            <stop offset="1" style={{ stopColor: ray.color, stopOpacity: 0 }} />
          </linearGradient>
        ))}

        <filter id={id('glow')} x="-10%" y="-40%" width="120%" height="180%">
          <feGaussianBlur stdDeviation="7" />
        </filter>
      </defs>

      {/* Light cone leaving the prism */}
      <g className="fan">
        <polygon
          points={`${ORIGIN.x},${ORIGIN.y} ${END_X},${fan[0].y} ${END_X},${fan[fan.length - 1].y}`}
          fill={`url(#${id('cone')})`}
          opacity="0.16"
          mask={`url(#${id('mask')})`}
        />
        {fan.map((ray) => (
          <g key={ray.y}>
            <line
              x1={ORIGIN.x}
              y1={ORIGIN.y}
              x2={END_X}
              y2={ray.y}
              stroke={`url(#${id(`ray-${ray.y}`)})`}
              strokeWidth="12"
              opacity="0.35"
              filter={`url(#${id('glow')})`}
            />
            <line
              x1={ORIGIN.x}
              y1={ORIGIN.y}
              x2={END_X}
              y2={ray.y}
              stroke={`url(#${id(`ray-${ray.y}`)})`}
              strokeWidth="1.6"
              strokeLinecap="round"
            />
          </g>
        ))}
      </g>

      {/* Incoming warm ray */}
      <path d={RAY_IN} stroke={`url(#${id('in')})`} strokeWidth="14" opacity="0.4" fill="none" filter={`url(#${id('glow')})`} />
      <path className="ray-in" d={RAY_IN} pathLength={1} stroke={`url(#${id('in')})`} strokeWidth="2.4" strokeLinecap="round" fill="none" />
      <path className="ray-pulse" d={RAY_IN} pathLength={1} stroke="white" strokeWidth="3.2" strokeLinecap="round" fill="none" />
    </svg>
  )
}
