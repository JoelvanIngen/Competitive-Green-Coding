import React, { useEffect, useRef, forwardRef } from 'react';
import hljs from 'highlight.js';

const CodeHighlight = forwardRef(({ code }, ref) => {
  const localRef = useRef(null);

  useEffect(() => {
    const target = ref?.current || localRef.current;
    if (target) {
      hljs.highlightElement(target);
    }
  }, [ref, code]);

  return (
    <pre className="row-[1] col-[1] p-8 leading-relaxed">
      <code ref={ref || localRef} className="language-c font-mono">
        {code}
      </code>
    </pre>
  );
});

export default CodeHighlight;
