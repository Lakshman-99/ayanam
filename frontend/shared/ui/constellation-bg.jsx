"use client";

import { useEffect, useRef } from "react";

const STAR_COUNT = 90;
const LINK_DISTANCE = 150;

function buildStars(width, height) {
  return Array.from({ length: STAR_COUNT }).map(() => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.12,
    vy: (Math.random() - 0.5) * 0.12,
    r: Math.random() * 1.4 + 0.4,
  }));
}

export default function ConstellationBg() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    let width = 0;
    let height = 0;
    let stars = [];
    let rafId = 0;
    let starColor = "rgba(255, 255, 255, 0.62)";
    let linkColor = "rgba(255, 255, 255, 0.16)";

    const updatePalette = () => {
      const styles = window.getComputedStyle(document.documentElement);
      const star = styles.getPropertyValue("--constellation-star").trim();
      const link = styles.getPropertyValue("--constellation-link").trim();
      starColor = star || "rgba(255, 255, 255, 0.62)";
      linkColor = link || "rgba(255, 255, 255, 0.16)";
    };

    const resize = () => {
      width = canvas.parentElement?.clientWidth || window.innerWidth;
      height = canvas.parentElement?.clientHeight || window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      stars = buildStars(width, height);
      updatePalette();
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < stars.length; i += 1) {
        const a = stars[i];

        a.x += a.vx;
        a.y += a.vy;

        if (a.x <= 0 || a.x >= width) {
          a.vx *= -1;
        }
        if (a.y <= 0 || a.y >= height) {
          a.vy *= -1;
        }

        ctx.beginPath();
        ctx.fillStyle = starColor;
        ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < stars.length; j += 1) {
          const b = stars[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const distance = Math.hypot(dx, dy);

          if (distance < LINK_DISTANCE) {
            const opacity = (1 - distance / LINK_DISTANCE) * 0.16;
            ctx.beginPath();
            ctx.strokeStyle = linkColor;
            ctx.globalAlpha = opacity;
            ctx.lineWidth = 1;
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
            ctx.globalAlpha = 1;
          }
        }
      }

      rafId = window.requestAnimationFrame(draw);
    };

    resize();
    draw();
    const observer = new MutationObserver(updatePalette);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    window.addEventListener("resize", resize);

    return () => {
      window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      observer.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="constellation-layer"
      aria-hidden="true"
    />
  );
}
