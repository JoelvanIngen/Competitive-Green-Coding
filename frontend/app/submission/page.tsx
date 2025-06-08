"use client";

import React, { useRef } from "react";
import { useSearchParams } from "next/navigation";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

import Markdown from "react-markdown";
import "./markdown.css";
import type { ImperativePanelHandle } from "react-resizable-panels";

// Dummy problems array for now
const dummyProblems = [
  {
    id: "1",
    content: `# Task\nYou will be given an array of numbers. You have to sort the odd numbers in ascending order while leaving the even numbers at their original positions.\n\n# Examples\n\`\`\`\n[7, 1]  =>  [1, 7]\n[5, 8, 6, 3, 4]  =>  [3, 8, 6, 5, 4]\n[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]  =>  [1, 8, 3, 6, 5, 4, 7, 2, 9, 0]\n\`\`\``,
  },
  {
    id: "2",
    content: `# Task\nFind the length of the longest increasing subsequence in an array.`,
  },
  {
    id: "3",
    content: `# Task\nImplement Kruskal's or Prim's algorithm to find MST.`,
  },
];

export default function Submission() {
  const panelLeft = useRef<ImperativePanelHandle | null>(null);
  const panelRight = useRef<ImperativePanelHandle | null>(null);

  const textarea = useRef<HTMLDivElement>(null);

  const searchParams = useSearchParams();
  const problemId = searchParams.get("id");

  const problem = dummyProblems.find((p) => p.id === problemId);

  const handleToggle = (panel: string) => {
    const panelRef = panel === "left" ? panelLeft : panelRight;

    if (panelRef.current) {
      if (panelRef.current.isCollapsed()) {
        panelRef.current.expand();
      } else {
        panelRef.current.collapse();
      }
    }
  };

  const sendCode = () => {
    let result = "";
    if (textarea.current) {
      textarea.current.childNodes.forEach((node: ChildNode) => {
        result += node.textContent + "\n";
      });
    }
    console.log(result);

    setTimeout(
      () =>
        alert(
          `Your program ran successfully!\nUser time: ${Math.floor(
            Math.random() * 100
          )} ms`
        ),
      1000
    );

    // Hier moet nog de juiste url komen.
    fetch("url???", {
      method: "POST",
      body: JSON.stringify({
        code: result,
        puid: problemId ?? "unknown",
      }),
    })
      .then((response) => response.json())
      .then((json) => console.log(json));
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col">
      <div className="m-4">
        <button onClick={() => handleToggle("left")}>Collapse</button>
        <button
          onClick={sendCode}
          className="px-2 bg-theme-primary rounded-sm float-right mr-4"
        >
          Run code
        </button>
      </div>
      <ResizablePanelGroup
        direction="horizontal"
        className="flex flex-col flex-1 min-h-0"
      >
        <ResizablePanel collapsible ref={panelLeft} defaultSize={40}>
          <div className="h-full bg-theme-text/5 mr-[3px] border-t-[5px] border-r-[5px] border-theme-text/10 rounded-tr-md">
            <div className="pl-8 pt-8 markdown">
              {problem ? (
                <Markdown>{problem.content}</Markdown>
              ) : (
                <p className="text-red-500 font-bold">
                  Oops, seems like your problem doesn&apos;t exist yet!
                </p>
              )}
            </div>
          </div>
        </ResizablePanel>
        <ResizableHandle className="invisible" />
        <ResizablePanel collapsible ref={panelRight} defaultSize={60}>
          <div className="h-full bg-theme-text/5 ml-[3px] border-t-[5px] border-l-[5px] border-theme-text/10 rounded-tl-md">
            <div
              ref={textarea}
              id="textarea"
              suppressContentEditableWarning={true}
              contentEditable
              className="text-lg pl-8 pt-8 h-full"
            >
              Input code here
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
