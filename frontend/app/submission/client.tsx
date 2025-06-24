"use client";

import React, { useRef, useState, useEffect, useActionState } from 'react';
import { submit, getResults } from './actions';

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

import { Button } from "@/components/ui/button";

import Markdown from 'react-markdown';
import './markdown.css';
import hljs from 'highlight.js';
import './highlight.css';
import rehypeHighlight from 'rehype-highlight';

export default function Submission({ data }: Props) {
    const panelLeft = useRef(null);
    const panelRight = useRef(null);
    const textarea = useRef(null);
    const highlight = useRef(null);
    const lineNumbers = useRef(null);
    const scroll = useRef(null);

    const [code, setCode] = useState(data.templateCode);
    const [codeResults, formAction, isPending] = useActionState(submit, {status: 0, message: "", submissionuuid: 0});

    const [results, setResults] = useState({hastested: false, error: '', desc: '', testspassed: 0, testsfailed: 0, cputime: 0});
    const resultsVisible = results.hastested ? '' : 'hidden';
    const resultsHidden = results.hastested ? 'hidden' : '';

    const [tab, setTab] = useState("problem");
    const tabBtnProblem = tab === 'problem' ? '' : 'ghost';
    const tabProblem = tab === 'problem' ? '' : 'hidden';
    const tabBtnOutput = tab === 'output' ? '' : 'ghost';
    const tabOutput = tab === 'output' ? '' : 'hidden';

    const [fetchingResults, setFetchingResults] = useState(false);
    const [fetchMessage, setFetchMessage] = useState("Submit your code to see results.");

    const difficultyStyle = data.difficulty === "Easy" ? "bg-green-200 text-green-800"
                                                    : data.difficulty === "Medium"
                                                    ? "bg-yellow-200 text-yellow-800"
                                                    : "bg-red-200 text-red-800"

    const parseCode = () => {
        return textarea.current.value ?? "";
    }

    const highlightCode = () => {       
        const solution = parseCode();
        const highlighted = hljs.highlight(solution, {language: 'python'}).value;
        highlight.current.innerHTML = highlighted;
        setCode(solution);
        handleLineNumbers(solution);
    }

    const insertAtCaret = (str: string, moveCaret: number = 0) => {
        const { value, selectionStart, selectionEnd } = textarea.current;
        textarea.current.value = `${value.substring(0, selectionEnd)}${str}${value.substring(selectionEnd)}`;
        textarea.current.selectionStart = textarea.current.selectionEnd = selectionStart + str.length - moveCaret;
    }

    const handleTab = (event) => {
        // Insert tabs
        if ((event.key) === 'Tab') {
            event.preventDefault();
            insertAtCaret('\t');    
        }
        // Automatic tabs when entering newline
        else if ((event.key) === 'Enter') {
            event.preventDefault();
            var textLines = textarea.current.value.substr(0, textarea.current.selectionStart).split("\n");
            var currentLineNumber = textLines.length;
            var line = textLines[currentLineNumber-1] || "";
            const match = line.match(/^[ \t]*/);

            // Scroll down on newline
            const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
            scroll.current.scrollTop += lineHeight;

            insertAtCaret('\n' + (match ? match[0] : ''));
        }
        // Bracket closing
        else if (['(', '{', '['].indexOf(event.key) > -1) {
            const pairs = {'(': ')', '{': '}', '[': ']'}
            event.preventDefault();
            insertAtCaret(event.key + pairs[event.key], 1);
        }
        highlightCode();
    }

    const handleSubmit = () => {
        setFetchMessage('Submitting solution...');
        setTab('output');
        panelLeft.current.expand();
        setFetchingResults(true);
    }

    const countLines = (str: string) => {
        if (str === '') return 0;
        return str.split('\n').length;
    }

    const handleLineNumbers = (solution: string) => {
        const lines = countLines(solution);

        const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
        const minLines = Math.floor(textarea.current.clientHeight / lineHeight) - 1;

        let spansHtml = '';
        for (let i = 1; i <= Math.max(lines, minLines); i++) {
            spansHtml += `<p>${i}</p>`;
        }
        lineNumbers.current.innerHTML = spansHtml;
    }

    // Syntax highlight on load
    useEffect(()=>{
        highlightCode();
        handleLineNumbers(parseCode());
    }, [])

    useEffect(()=>{
        textarea.current.value = code;
    }, [isPending])

    // Fetch code results if submission is successfull.
    useEffect( () => {
        async function loadResults() {
            if (codeResults.status == 200) {
                const form = new FormData();
                form.append('problemId', data.pid);

                const result = await getResults(null, form);
                setResults(result);
            }
            setFetchingResults(false);
            console.log(fetchingResults, 'result');
        }
        loadResults();
    }, [codeResults])

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

    return (
        <form onSubmit={handleSubmit} action={formAction} className="h-[calc(100vh-64px)] flex flex-col ml-4 mr-4 overflow-hidden">
            <input type='hidden' name='problemId' defaultValue={data.pid}></input>
            <div className="ml-8 mr-8">
                <div>
                    <h1 className="text-theme-text font-bold text-2xl mb-2 inline">{data.name}</h1>
                    <p className={`${difficultyStyle} ml-6 inline-block pr-2 pl-2 text-center rounded-sm`}>{data.difficulty}</p>
                    <p className="ml-2 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{data.language}</p>
                    {data.tags.map((tag, index)=>(<p key={index} className="ml-2 inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{tag}</p>))}
                </div>
                <div className="mt-2 mb-2">
                    <Button type='button' variant={tabBtnProblem || 'default'} className='outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'problem' ? handleToggle('left') : setTab('problem')}>problem</Button>
                    <Button type='button' variant={tabBtnOutput || 'default'} className='ml-2 outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'output' ? handleToggle('left') : setTab('output')}>output</Button>                    
                    <Button className='float-right bg-theme-primary hover:bg-theme-primary-dark' type='submit' disabled={fetchingResults}>Run code</Button>
                </div>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0 mb-4'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40}>
                    <div className="h-full bg-card mr-[3px] rounded-xl border shadow-sm overflow-y-auto min-scroll overflow-x-auto">
                        <div className='grid p-6'>
                            <div className={`markdown row-[1] col-[1] z-1 ${tabProblem}`}>
                                <Markdown rehypePlugins={[rehypeHighlight]}>{data.longDesc}</Markdown>
                            </div>
                            <div className={`row-[1] col-[1] ${tabOutput}`}>
                                <div className={resultsHidden}>
                                    {/* <h2 className='font-bold'>Submit log</h2> */}
                                    <p>{fetchMessage}</p>
                                    <p>{codeResults.message}</p>
                                </div>
                                <div>
                                    <p className={`whitespace-nowrap ${resultsVisible}`}>
                                        <span className='font-bold'>CPU-Time:</span> {results.cputime}
                                        <span className='font-bold ml-4'>Tests passed:</span> {results.testspassed}
                                        <span className='font-bold ml-4'>Tests failed:</span> {results.testsfailed}
                                        <br/>
                                        <span>{results.desc}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle className='invisible'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60}>
                    <div spellCheck="false" ref={scroll} className="min-scroll text-[0.8rem] h-full grid grid-cols-[3rem_1fr] bg-card ml-[3px] rounded-xl border shadow-sm overflow-x-auto overflow-y-auto">
                        <div ref={lineNumbers} className='row[1] col-[1] pl-4 pt-4 font-code text-left leading-relaxed whitespace-pre text-theme-text/50'>
                            <p>1</p><p>2</p>
                        </div>
                        <textarea name='code' ref={textarea} className="font-code resize-none overflow-hidden whitespace-pre text-transparent outline-none z-1 row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed" style={{caretColor: "var(--theme-primary)"}} id="textare" onKeyDown={handleTab} onInput={highlightCode} defaultValue={data.templateCode}></textarea>
                        <pre className="row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed">
                            <code ref={highlight} className="line-numbers font-code"></code>
                        </pre>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </form>
    );
}
