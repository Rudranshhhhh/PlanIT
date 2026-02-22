import { useEffect, useRef, useState } from 'react';

const SplitText = ({
  text,
  className = '',
  delay = 50,
  duration = 1.25,
  ease = 'ease-out',
  splitType = 'chars',
  from = { opacity: 0, y: 40 },
  to = { opacity: 1, y: 0 },
  threshold = 0.1,
  rootMargin = '-100px',
  textAlign = 'left',
  onLetterAnimationComplete,
  showCallback = false,
}) => {
  const containerRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [animatedCount, setAnimatedCount] = useState(0);

  useEffect(() => {
    let observer;
    
    // Use requestAnimationFrame to ensure DOM is ready and transitions work
    const checkVisibility = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        if (isInViewport) {
          // Small delay to ensure initial styles are applied before transition
          setTimeout(() => {
            setIsVisible(true);
          }, 50);
        }
      }
    };

    requestAnimationFrame(() => {
      checkVisibility();

      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setTimeout(() => {
                setIsVisible(true);
              }, 50);
            }
          });
        },
        {
          threshold: threshold,
          rootMargin: rootMargin,
        }
      );

      if (containerRef.current) {
        observer.observe(containerRef.current);
      }
    });

    return () => {
      if (observer && containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, [threshold, rootMargin]);

  const splitText = () => {
    if (splitType === 'chars') {
      return text.split('').map((char, index) => {
        if (char === ' ') {
          return <span key={index} style={{ display: 'inline-block', width: '0.25em' }}>&nbsp;</span>;
        }
        const charIndex = text.substring(0, index).replace(/\s/g, '').length;
        return (
          <span
            key={index}
            className="split-char"
            style={{
              display: 'inline-block',
              opacity: isVisible ? to.opacity : from.opacity,
              transform: isVisible
                ? `translateY(${to.y}px)`
                : `translateY(${from.y}px)`,
              transition: isVisible 
                ? `opacity ${duration}s ${ease} ${charIndex * delay}ms, transform ${duration}s ${ease} ${charIndex * delay}ms`
                : 'none',
            }}
            onTransitionEnd={() => {
              if (isVisible) {
                setAnimatedCount((prev) => {
                  const newCount = prev + 1;
                  if (showCallback && onLetterAnimationComplete && newCount === text.replace(/\s/g, '').length) {
                    onLetterAnimationComplete();
                  }
                  return newCount;
                });
              }
            }}
          >
            {char}
          </span>
        );
      });
    } else if (splitType === 'words') {
      return text.split(' ').map((word, wordIndex) => (
        <span
          key={wordIndex}
          className="split-word"
          style={{
            display: 'inline-block',
            marginRight: '0.25em',
            opacity: isVisible ? to.opacity : from.opacity,
            transform: isVisible
              ? `translateY(${to.y}px)`
              : `translateY(${from.y}px)`,
            transition: isVisible
              ? `opacity ${duration}s ${ease} ${wordIndex * delay}ms, transform ${duration}s ${ease} ${wordIndex * delay}ms`
              : 'none',
          }}
        >
          {word}
        </span>
      ));
    }
    return text;
  };

  const alignStyle = {
    textAlign: textAlign,
  };

  return (
    <span
      ref={containerRef}
      className={className}
      style={alignStyle}
    >
      {splitText()}
    </span>
  );
};

export default SplitText;
