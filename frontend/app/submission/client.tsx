/**
 * File: client.tsx
 * Route: /submission?id=[id]
 * Description:
 * Client-side component that renders the submission page. Handles client side
 * logic and event-handling for code submission.
 * Component type: Client component
 */

"use client";

import React, { useRef, useState, useEffect, useActionState } from 'react';
import { submit, getResults, fetchResult } from './actions';

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

interface Props {
  data: {
    templateCode: string;
    difficulty: string;
    pid: string;
    name: string;
    language: string;
    tags: string[];
    longDesc: string;
    prevSubmission: boolean;
  },
  subData: {
    hastested: boolean;
    error: string;
    errormsg: string;
    testspassed: boolean;
    cputime: number;
    energyusage: number;
    emissions: number;
    submission: string;
    };
}

/** Calculates number of metres a car has to drive to produce emissions g CO_2.
 *  Based on emission rate of 106.4 g CO_2 / km = 106.4 mg CO_2 / m provided by:
 *  https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger
 */
function calculateCarDistance(emissions: number) {
  return emissions / 106.4;
}

export default function Submission({ data, subData }: Props) {
    const panelLeft = useRef<any>(null);
    const panelRight = useRef<any>(null);
    const textarea = useRef<HTMLTextAreaElement>(null);
    const highlight = useRef<HTMLElement>(null);
    const lineNumbers = useRef<HTMLDivElement>(null);
    const scroll = useRef<HTMLDivElement>(null);

    const [code, setCode] = useState(data.templateCode);
    const [codeResults, formAction, isPending] = useActionState(submit, {status: 0, message: "", submissionuuid: 0});

    const [results, setResults] = useState(subData);

    const [seeResults, setSeeResults] = useState(false);
    const resultsVisible = seeResults ? '' : 'hidden';
    const resultsHidden = seeResults ? 'hidden' : '';
    
    const [tab, setTab] = useState("problem");
    const tabBtnProblem = tab === 'problem' ? '' : 'ghost';
    const tabProblem = tab === 'problem' ? '' : 'hidden';
    const tabBtnOutput = tab === 'output' ? '' : 'ghost';
    const tabOutput = tab === 'output' ? '' : 'hidden';

    const [fetchingResults, setFetchingResults] = useState(false);
    const [fetchMessage, setFetchMessage] = useState("Submit your code to see results.");

    const difficultyStyle = data.difficulty === "easy" ? "bg-green-200 text-green-800"
                                                    : data.difficulty === "medium"
                                                    ? "bg-yellow-200 text-yellow-800"
                                                    : "bg-red-200 text-red-800"

    const [testResultsHeader, setTestResultsHeader] = useState(<p></p>);

    const [fetchingMessage, setFetchingMessage] = useState(['', '']);

    // Get current code of user
    const parseCode = () => {
        return textarea.current?.value ?? "";
    }

    // Highlight code (not optimized due to bugs)
    const highlightCode = () => {
        const solution = parseCode();

        if (textarea.current && highlight.current) {
            const highlighted = hljs.highlight(solution, {language: data.language}).value;
            highlight.current.innerHTML = highlighted;
        }

        setCode(solution);
        handleLineNumbers(solution);
        setSubmissionCookie(data.pid, parseCode());
        subData.submission = solution;
    }

    // Insert string at current position in textarea
    const insertAtCaret = (str: string, moveCaret: number = 0) => {
        if (!textarea.current) return;
        const { value, selectionStart, selectionEnd } = textarea.current;
        textarea.current.value = `${value.substring(0, selectionEnd)}${str}${value.substring(selectionEnd)}`;
        textarea.current.selectionStart = textarea.current.selectionEnd = selectionStart + str.length - moveCaret;
    }

    // Code editor key evnent handlers
    const handleTab = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Insert tabs
        if ((event.key) === 'Tab') {
            event.preventDefault();
            insertAtCaret('\t');    
        }
        // Automatic tabs when entering newline
        else if ((event.key) === 'Enter') {
            event.preventDefault();
            if (!textarea.current) return;
            var textLines = textarea.current.value.substr(0, textarea.current.selectionStart).split("\n");
            var currentLineNumber = textLines.length;
            var line = textLines[currentLineNumber-1] || "";
            const match = line.match(/^[ \t]*/);

            // Scroll down on newline
            if (textarea.current && scroll.current) {
                const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
                scroll.current.scrollTop += lineHeight;
            }

            insertAtCaret('\n' + (match ? match[0] : ''));
        }
        // Bracket closing
        else if (['(', '{', '['].indexOf(event.key) > -1) {
            const pairs: { [key: string]: string } = {'(': ')', '{': '}', '[': ']'};
            event.preventDefault();
            insertAtCaret(event.key + pairs[event.key], 1);
        }
        highlightCode();
    }

    // Perform additional actions on submit
    const handleSubmit = () => {
        setSeeResults(false);
        setFetchMessage('Submitting solution...');
        setTab('output');
        if (panelLeft.current) {
            panelLeft.current.expand();
            panelLeft.current.resize(50);
        }
        setFetchingResults(true);
    }

    const countLines = (str: string) => {
        if (str === '') return 0;
        return str.split('\n').length;
    }

    // Show line numbers
    const handleLineNumbers = (solution: string) => {
        const lines = countLines(solution);

        if (!textarea.current || !lineNumbers.current) return;

        const lineHeight = parseFloat(window.getComputedStyle(textarea.current).lineHeight);
        const minLines = Math.floor(textarea.current.clientHeight / lineHeight) - 1;

        let spansHtml = '';
        for (let i = 1; i <= Math.max(lines, minLines); i++) {
            spansHtml += `<p>${i}</p>`;
        }
        lineNumbers.current.innerHTML = spansHtml;
    }

    // Save current problem_id and code in cookie
    function setSubmissionCookie(id: string, code: string) {
        const json = JSON.stringify({
            id: id,
            code: code
        });

        const name = "submission"

        const expires = new Date()
        expires.setDate(expires.getDate() + 1)
        document.cookie = `${name}=${json}; expires=${expires.toUTCString()}; path=/`
    }

    const cookieRegex = /submission=\{"id":"(\d+)","code":"(.*?)"\}/;

    const getCookie = () => {
        const cookie = document.cookie.match(cookieRegex);
        if (cookie === null) {
            return [null, '', ''];
        }
        return cookie;
    }

    // Get code saved in cookie if possible, on reload
    useEffect(()=>{
        const cookie = getCookie();
        if (cookie[1] === data.pid) {
            if (textarea.current) {
                let code = cookie[2] ? cookie[2] : '';
                textarea.current.value = code.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
            }
        }
        highlightCode();
        handleLineNumbers(parseCode());
    }, [])

    const loadTemplateCode = () => {
        if (textarea.current) {
            textarea.current.value = data.templateCode;
            highlightCode();
            handleLineNumbers(parseCode());
            setSeeResults(true);
        }
    }

    useEffect(()=>{
        const cookie = getCookie();
        if (cookie[1] === data.pid) {
            if (textarea.current) {
                let code = cookie[2] ? cookie[2] : '';
                textarea.current.value = code.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
            }     
        }
        highlightCode();
        handleLineNumbers(parseCode());
    }, [isPending])

    // Fetch code results if submission is successfull.
    useEffect( () => {
        async function loadResults() {
            if (codeResults.status === 201) {
                setFetchingMessage(['Running your code...', 'This may take a while.']);
                const form = new FormData();
                form.append('submissionuuid', codeResults.submissionuuid);
                const result = await getResults(null, form);
                setResults(result);

                if (result.testspassed) {
                    setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-green-800'>✅Tests passed✅</span></p>);
                }
                else {
                    console.log('Result error:', result.error);

                    switch (result.error) {
                        case "tests_failed":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>❌Tests failed❌</span></p>);
                            break;
                        case "mem_limit":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>💾Memory error💾</span></p>);
                            break;
                        case "timeout":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>⏳Timeout error⏳</span></p>);
                            break;
                        case "security":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>🔒Security error🔒</span></p>);
                            break;
                        case "compile_error":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>🛠️Compiler error🛠️</span></p>);
                            break;
                        case "runtime_error":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>⚠️Runtime error⚠️</span></p>);
                            break;
                        case "internal_error":
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>❌Internal error❌</span></p>);
                            break;
                        default:
                            setTestResultsHeader(<p><span className='pl-4 pr-2 pb-4 font-bold mr-2 text-red-800'>Something went wrong</span></p>);
                            break;
                    }
                }
                setSeeResults(true);             
                }
            }
            setFetchingResults(false);
            setFetchingMessage(['','']);
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
        <form onSubmit={handleSubmit} action={formAction} className="h-[calc(100vh-82px)] flex flex-col ml-4 mr-4 overflow-hidden">
            <input type='hidden' name='problemId' defaultValue={data.pid}></input>
            <input type='hidden' name='language' defaultValue={data.language}></input>
            <div className="ml-8 mr-8 mt-2">
                <div>
                    <h1 className="text-theme-text font-bold text-2xl mb-2 inline">{data.name}</h1>
                    <p className={`${difficultyStyle} ml-6 w-fit inline-block pr-2 pl-2 text-center rounded-sm`}>{data.difficulty}</p>
                    <p className="ml-2 w-fit inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{data.language}</p>
                    {data.tags.map((tag, index)=>(<p key={index} className="ml-2 w-fit inline-block pr-2 pl-2 text-center bg-theme-text/10 rounded-sm">{tag}</p>))}
                </div>
                <div className="mt-2 mb-2">
                    <Button type='button' variant={tabBtnProblem || 'default'} className='outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'problem' ? handleToggle('left') : setTab('problem')}>problem</Button>
                    <Button type='button' variant={tabBtnOutput || 'default'} className='ml-2 outline-1 hover:outline-solid outline-theme-text' onClick={() => tab === 'output' ? handleToggle('left') : setTab('output')}>output</Button>                
                    <Button className='float-right bg-theme-primary hover:bg-theme-primary-dark' type='submit' disabled={fetchingResults}>Run code</Button>
                    <Button variant='ghost' type='button' onClick={loadTemplateCode} className='outline-1 hover:outline-solid outline-theme-text float-right mr-4'>Get template code</Button>: <Button className='hidden' type='button'></Button>
                </div>
            </div>
            <ResizablePanelGroup direction='horizontal' className='flex flex-col flex-1 min-h-0 mb-4'>
                <ResizablePanel collapsible ref={panelLeft} defaultSize={40} minSize={10}>
                    <div className="bg-card h-full mr-[3px] rounded-xl border shadow-sm overflow-y-auto min-scroll overflow-x-auto">
                        <div className='grid p-6'>
                            <div className={`markdown row-[1] col-[1] z-1 ${tabProblem}`}>
                                <Markdown rehypePlugins={[rehypeHighlight]}>{data.longDesc}</Markdown>
                            </div>
                            <div className={`row-[1] col-[1] ${tabOutput}`}>
                                <div className={resultsHidden}>
                                    <p className="text-transparent w-fit bg-clip-text animate-gradient font-bold bg-gradient-to-r from-theme-primary to-theme-text">{fetchMessage}</p>
                                    <p className='font-bold'>{codeResults.message}</p>
                                    <p className="text-transparent w-fit bg-clip-text animate-gradient font-bold bg-gradient-to-r from-theme-primary to-theme-text">{fetchingMessage[0]}</p>
                                    <p className='font-bold'>{fetchingMessage[1]}</p>
                                </div>
                                <div>
                                    <div className={`whitespace-nowrap ${resultsVisible}`}>
                                        <div className='flex flex-wrap flex-[40%] justify-around mb-2'>
                                            <>{testResultsHeader}</>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-yellow-800'>⚡CPU time:</span> 
                                                <span>{results.cputime ? results.cputime.toFixed(5) : 0} ms</span>
                                            </p>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-green-800'>🔋Energy usage:</span> 
                                                <span>{results.energyusage ? (results.energyusage * 3600000).toFixed(5) : 0} Joule</span>
                                            </p>
                                            <p>    
                                                <span className='pl-4 pr-2 pb-4 text-center font-bold text-blue-800'>🌍Carbon emissions:</span> 
                                                <span>{results.emissions ? (results.emissions * 1000000).toFixed(5) : 0} mg CO₂ (equivalent to travelling </span>
                                                <span className='underline text-stone-500 dark:text-stone-300'><a href="https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger">{results.emissions ? (calculateCarDistance(results.emissions * 1000000)).toFixed(5) : 0} m</a></span>
                                                <span> by car)</span>
                                            </p>
                                        </div>
                                        <p className='text-center text-xs border-b-1 border-theme-text'>    
                                                <span className='text-gray-500'><a href="https://codecarbon.io/">Measured using <span className='text-gray-400 underline'>CodeCarbon</span></a></span>
                                        </p>
                                        <span className='mt-2 whitespace-pre-line'>{results.errormsg}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ResizablePanel>
                <ResizableHandle withHandle className='bg-theme-bg'/>
                <ResizablePanel collapsible ref={panelRight} defaultSize={60} minSize={20}>
                    <div spellCheck="false" ref={scroll} className="min-scroll text-[0.8rem] h-full grid grid-cols-[3rem_1fr] bg-card ml-[3px] rounded-xl border shadow-sm overflow-x-auto overflow-y-auto">
                        <div ref={lineNumbers} className='row[1] col-[1] pl-4 pt-4 font-code text-left leading-relaxed whitespace-pre text-theme-text/50'>
                            <p>1</p><p>2</p>
                        </div>
                        <textarea name='code' ref={textarea} className="font-code resize-none overflow-hidden whitespace-pre text-transparent outline-none z-1 row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed" style={{caretColor: "var(--theme-primary)"}} id="textare" onKeyDown={handleTab} onInput={highlightCode} defaultValue={subData.submission}></textarea>
                        <pre className="row-[1] col-[2] pt-4 pr-8 pb-8 leading-relaxed">
                            <code ref={highlight} className="line-numbers font-code"></code>
                        </pre>
                    </div>
                </ResizablePanel>
            </ResizablePanelGroup>
        </form>
    );
}
