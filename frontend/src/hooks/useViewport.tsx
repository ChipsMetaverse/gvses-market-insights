import { useEffect, useState } from 'react';

const MOBILE_BREAKPOINT = 768;

type ViewportState = {
  width: number;
  height: number;
  isMobile: boolean;
};

const getInitialState = (): ViewportState => {
  if (typeof window === 'undefined') {
    return {
      width: MOBILE_BREAKPOINT + 1,
      height: 1024,
      isMobile: false,
    };
  }

  return {
    width: window.innerWidth,
    height: window.innerHeight,
    isMobile: window.innerWidth <= MOBILE_BREAKPOINT,
  };
};

export const useViewport = (): ViewportState => {
  const [state, setState] = useState<ViewportState>(() => getInitialState());

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const mediaQuery = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`);

    const handleChange = () => {
      setState({
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: mediaQuery.matches,
      });
    };

    handleChange();

    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      mediaQuery.addListener(handleChange);
    }

    window.addEventListener('resize', handleChange);

    return () => {
      if (typeof mediaQuery.removeEventListener === 'function') {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        mediaQuery.removeListener(handleChange);
      }
      window.removeEventListener('resize', handleChange);
    };
  }, []);

  return state;
};
