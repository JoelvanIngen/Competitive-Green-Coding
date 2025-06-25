import React, { useEffect, useRef, forwardRef } from 'react';
import hljs from 'highlight.js';

interface CodeHighlightProps {
  code: string;
}

const CodeHighlight = forwardRef<HTMLElement, CodeHighlightProps>(({ code }, ref) => {
  const localRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const target = localRef.current;
    if (target) {
      hljs.highlightElement(target);
    }
  }, [code]);

  return (
    <pre className="row-[1] col-[1] p-8 leading-relaxed">
      <code 
        ref={(element) => {
          localRef.current = element;
          if (typeof ref === 'function') {
            ref(element);
          } else if (ref) {
            ref.current = element;
          }
        }} 
        className="language-c font-mono"
      >
        {code}
      </code>
    </pre>
  );
});

CodeHighlight.displayName = 'CodeHighlight';

export default CodeHighlight;
