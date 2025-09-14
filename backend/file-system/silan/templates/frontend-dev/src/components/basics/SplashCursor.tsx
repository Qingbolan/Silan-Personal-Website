import React, { useRef, useEffect, useCallback } from 'react';

interface SplashCursorProps {
  enabled?: boolean;
  intensity?: number;
  color?: string;
  size?: number;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  opacity: number;
}

const SplashCursor: React.FC<SplashCursorProps> = ({
  enabled = true,
  intensity = 0.5,
  color,
  size = 3
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: 0, y: 0, prevX: 0, prevY: 0 });

  // Get the theme primary color from CSS custom properties
  const getThemePrimaryColor = useCallback(() => {
    if (typeof window !== 'undefined') {
      return getComputedStyle(document.documentElement).getPropertyValue('--color-primary') || '#0066FF';
    }
    return '#0066FF';
  }, []);

  const createParticle = useCallback((x: number, y: number, vx: number, vy: number): Particle => {
    return {
      x,
      y,
      vx: vx * (0.5 + Math.random() * 0.5),
      vy: vy * (0.5 + Math.random() * 0.5),
      life: 1,
      maxLife: 20 + Math.random() * 40,
      size: size * (0.5 + Math.random() * 0.5),
      opacity: 0.8 + Math.random() * 0.2
    };
  }, [size]);

  const updateParticles = useCallback(() => {
    const particles = particlesRef.current;
    
    for (let i = particles.length - 1; i >= 0; i--) {
      const particle = particles[i];
      
      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;
      
      // Apply friction
      particle.vx *= 0.98;
      particle.vy *= 0.98;
      
      // Update life
      particle.life -= 1;
      particle.opacity = particle.life / particle.maxLife;
      
      // Remove dead particles
      if (particle.life <= 0) {
        particles.splice(i, 1);
      }
    }
  }, []);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas with fade effect
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Render particles
    const particles = particlesRef.current;
    const particleColor = color || getThemePrimaryColor();
    
    particles.forEach(particle => {
      ctx.save();
      ctx.globalAlpha = particle.opacity;
      
      // Create gradient for glow effect
      const gradient = ctx.createRadialGradient(
        particle.x, particle.y, 0,
        particle.x, particle.y, particle.size * 2
      );
      gradient.addColorStop(0, particleColor);
      gradient.addColorStop(1, 'transparent');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.restore();
    });
  }, [color, getThemePrimaryColor]);

  const animate = useCallback(() => {
    updateParticles();
    render();
    animationRef.current = requestAnimationFrame(animate);
  }, [updateParticles, render]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!enabled) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const prevX = mouseRef.current.x;
    const prevY = mouseRef.current.y;
    
    mouseRef.current.x = x;
    mouseRef.current.y = y;
    
    // Calculate velocity
    const vx = (x - prevX) * intensity;
    const vy = (y - prevY) * intensity;
    const speed = Math.sqrt(vx * vx + vy * vy);
    
    // Create particles based on movement speed
    if (speed > 1) {
      const numParticles = Math.min(Math.floor(speed / 5), 5);
      
      for (let i = 0; i < numParticles; i++) {
        const particle = createParticle(
          x + (Math.random() - 0.5) * 10,
          y + (Math.random() - 0.5) * 10,
          vx + (Math.random() - 0.5) * 2,
          vy + (Math.random() - 0.5) * 2
        );
        particlesRef.current.push(particle);
      }
    }
  }, [enabled, intensity, createParticle]);

  const handleClick = useCallback((e: MouseEvent) => {
    if (!enabled) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Create burst of particles on click
    for (let i = 0; i < 15; i++) {
      const angle = (Math.PI * 2 * i) / 15;
      const speed = 2 + Math.random() * 3;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed;
      
      const particle = createParticle(x, y, vx, vy);
      particle.maxLife *= 1.5; // Make burst particles last longer
      particlesRef.current.push(particle);
    }
  }, [enabled, createParticle]);

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }, []);

  useEffect(() => {
    if (!enabled) return;
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('click', handleClick);
    
    // Start animation loop
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('click', handleClick);
      
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [enabled, resizeCanvas, handleMouseMove, handleClick, animate]);

  if (!enabled) return null;

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-50 mix-blend-screen opacity-80"
    />
  );
};

export default SplashCursor; 