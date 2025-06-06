"use client";

import React, { useRef, useState } from 'react';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

import Markdown from 'react-markdown';
import './markdown.css';
import hljs from 'highlight.js';
import './highlight.css';
import rehypeHighlight from 'rehype-highlight';

import CodeHighlight  from '@/components/codeHighlight';

const initContent = `# Task
You will be given an array of numbers. You have to sort the odd numbers in ascending order while leaving the even numbers at their original positions.

# Examples
~~~
[7, 1]  =>  [1, 7]
[5, 8, 6, 3, 4]  =>  [3, 8, 6, 5, 4]
[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]  =>  [1, 8, 3, 6, 5, 4, 7, 2, 9, 0]
~~~

~~~c
int main(void) {
    int x = 10;
}
~~~
`

const initCode = `int sort_odd(int n) {
    // Here comes your code.
}
`


export default function Submission() {
    const panelLeft = useRef(null);
    const panelRight = useRef(null);

    const handleToggle = (panel: string) => {
        const panelRef = panel == 'left' ? panelLeft : panelRight;

        if (panelRef.current) {
            if (panelRef.current.isCollapsed()) {
                panelRef.current.expand();
            } else {
                panelRef.current.collapse();
            }
        }
    }

    const textarea = useRef(null);

    const parseCode = () => {
        let result = '';
        if (textarea.current) {
            textarea.current.childNodes.forEach((node) => {
                result += node.textContent + '\n';
            })
        }
        return result;
    }

    const sendCode = () => {
        // Hier moet nog de juiste url komen.
        const code = parseCode();
        console.log(code);

        fetch('url???', {
            method: "POST",
            body: JSON.stringify({
                code: code,
                puid: '1'
            })
        }).then((response) => response.json()).then((json) => console.log(json))
    }

    const highlight = useRef(null);
    const onInput = () => {
        const highlighted = hljs.highlight(parseCode(), {language: 'c'}).value;
        highlight.current.innerHTML = highlighted;
    }

    return (
        <div className="min-h-[calc(100vh-64px)] flex flex-col"> 
            <div className="bg-theme-primary/50">
            <button onClick={() => handleToggle('left')}>Collapse</button>
            <button onClick={sendCode} className='px-2 bg-theme-primary rounded-sm float-right mr-4'>Run code</button>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40}>
                    <div className="h-full bg-theme-text/5 mr-[3px] border-t-[5px] border-r-[5px] border-theme-text/10 rounded-tr-md overflow-x-hidden">
                        <div className="pl-8 pt-8 markdown">
                            <Markdown rehypePlugins={[rehypeHighlight]}>{initContent}</Markdown>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle className='invisible'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60}>
                    <div spellCheck="false" className="min-scroll text-[0.8rem] grid h-full bg-theme-text/5 ml-[3px] border-t-[5px] border-l-[5px] border-theme-text/10 rounded-tl-md overflow-x-auto">
                        <div ref={textarea} style={{caretColor: "var(--theme-primary)" }} id="textarea" onInput={onInput} suppressContentEditableWarning={true} contentEditable className="whitespace-pre text-transparent font-mono outline-none z-1 row-[1] col-[1] pl-8 pt-8">{initCode}</div>
                        <CodeHighlight ref={highlight} code={initCode}></CodeHighlight>
                    </div>
                </ResizablePanel>   
            </ResizablePanelGroup>
        </div>
    );
}
