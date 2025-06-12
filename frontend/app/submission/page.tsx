"use client";

import React, { useRef, useState, useEffect } from 'react';
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

const initContent = `# Problem:
Given an array of integers, write a function to find and return the maximum value in the array.

# Input:
- An integer array \`arr\`
- The size of the array \`n\`

# Output:
- The maximum integer value in the array

# Example:
~~~
[3, 1, 4, 2] -> 4
~~~
`

const data = {
    pid: 1,
    name: 'Find maximum integer',
    language: 'c',
    difficulty: 'Easy',
    tags: ['array'],
    shortDesc: 'Find the maximum integer.',
    longDesc: initContent,
    funcSignature: 'int findMax(int arr[], int n)',
    templateCode: ' {\n   // Here comes your code.\n}'
}

export default function Submission() {
    const panelLeft = useRef(null);
    const panelRight = useRef(null);
    const textarea = useRef(null);
    const funcSignature = useRef(null);
    const highlight = useRef(null);

    const [tab, setTab] = useState("problem");
    const tabBtnProblem = tab === 'problem' ? 'bg-theme-primary' : 'bg-theme-bg';
    const tabProblem = tab === 'problem' ? 'visible' : 'invisible';
    const tabBtnOutput = tab === 'output' ? 'bg-theme-primary' : 'bg-theme-bg';
    const tabOutput = tab === 'output' ? 'visible' : 'invisible';

    const funcLength = data.funcSignature.length;

    const difficultyStyle = data.difficulty === "Easy" ? "bg-green-200 text-green-800"
                                                    : data.difficulty === "Medium"
                                                    ? "bg-yellow-200 text-yellow-800"
                                                    : "bg-red-200 text-red-800"

    const highlightCode = (event) => {
        // if (textarea.current.value.length < funcLength) {
        //     textarea.current.value = data.funcSignature;
        // }

        const highlighted = hljs.highlight(parseCode(), {language: 'c'}).value;
        highlight.current.innerHTML = highlighted;
    }

    const handleTab = (event) => {
        if ((event.key) === 'Tab') {
            event.preventDefault();
            const area = textarea.current;
            const { value, _, selectionEnd } = textarea.current;
            textarea.current.value = `${value.substring(0, selectionEnd)}\t${value.substring(selectionEnd)}`;
        }
    }

    // Syntax highlight on reload
    useEffect(()=>{
        highlightCode();
    }, [])

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
    
    const parseCode = () => {
        return textarea.current.value ?? "";
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

    return (
        <div className="h-[calc(100vh-64px)] flex flex-col ml-4 mr-4 overflow-hidden"> 
            <div className="ml-8 mr-8">
                <div>
                    <h1 className="text-theme-text font-bold text-2xl mb-2 inline">{data.name}</h1>
                    <p className={`${difficultyStyle} ml-4 inline-block pr-2 pl-2 text-center rounded-sm`}>{data.difficulty}</p>
                    <p className="ml-4 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{data.language}</p>
                    {data.tags.map(tag=>(<p className="ml-4 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{tag}</p>))}
                </div>
                <div className="mt-2">
                    <button onClick={() => tab === 'problem' ? handleToggle('left') : setTab('problem')} className={`mb-2 mr-2 px-2 rounded-md ${tabBtnProblem}`}>Problem</button>
                    <button onClick={() => tab === 'output' ? handleToggle('left') : setTab('output')} className={`px-2 rounded-md ${tabBtnOutput}`}>Output</button>
                    <button onClick={sendCode} className='px-2 bg-theme-primary rounded-md float-right'>Run code</button>
                </div>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0 mb-4'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40}>
                    <div className="h-full bg-theme-text/5 mr-[3px] border-[5px] border-theme-text/10 rounded-md overflow-y-auto min-scroll overflow-x-auto">
                        <div className='grid p-8'>
                            <div className={`markdown row-[1] col-[1] ${tabProblem}`}>
                                <Markdown rehypePlugins={[rehypeHighlight]}>{data.longDesc}</Markdown>
                            </div>
                            <div className={`row-[1] col-[1] ${tabOutput}`}>No test results yet.</div>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle className='invisible'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60}>
                    <div spellCheck="false" className="min-scroll text-[0.8rem] h-full grid bg-theme-text/5 ml-[3px] border-[5px] border-theme-text/10 rounded-md overflow-x-auto overflow-y-auto">
                        {/* <div className="row[1] col[1] bg-red-300">jfaksljfjdsklfj</div> */}
                        <textarea ref={textarea} className="font-code resize-none overflow-hidden whitespace-pre text-transparent outline-none z-1 row-[1] col-[1] p-8 leading-relaxed" style={{caretColor: "var(--theme-primary)"}} id="textare" onKeyDown={handleTab} onInput={highlightCode} defaultValue={data.funcSignature + data.templateCode}></textarea>
                        {/* <div className="row-[1] col-[1] z-1 p-8 leading-relaxed">
                            <textarea ref={funcSignature} readOnly className="bg-red-400 w-full font-code resize-none overflow-hidden whitespace-pre text-white outline-none" defaultValue={data.funcSignature}></textarea>
                            <textarea ref={textarea} className="bg-blue-400 h-full w-full font-code resize-none overflow-hidden whitespace-pre text-white outline-none" style={{caretColor: "var(--theme-primary)"}} onInput={highlightCode} defaultValue={data.templateCode}></textarea>
                        </div> */}
                        <pre className="row-[1] col-[1] p-8 leading-relaxed">
                            <code ref={highlight} className="line-numbers font-code"></code>
                        </pre>
                    </div>
                </ResizablePanel>   
            </ResizablePanelGroup>
        </div>
    );
}
