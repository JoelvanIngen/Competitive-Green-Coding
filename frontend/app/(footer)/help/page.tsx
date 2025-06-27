// -----------------------------------------------------------------------------
// help.tsx (HelpPage)
//
// Static FAQ page using an accordion UI.
// Provides answers to common questions about the GreenCode platform.
// -----------------------------------------------------------------------------

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

export default function HelpPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 text-theme-text">
      <h1 className="text-3xl font-bold mb-8">Frequently Asked Questions</h1>
      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="item-1">
          <AccordionTrigger>What is GreenCode?</AccordionTrigger>
          <AccordionContent>
            GreenCode is a competitive coding platform focused on low-power, efficient programming challenges.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>Do I need an account to submit code?</AccordionTrigger>
          <AccordionContent>
            Yes. You need to create an account to track submissions and participate in leaderboards.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-3">
          <AccordionTrigger>What languages are supported?</AccordionTrigger>
          <AccordionContent>
            Currently, we support C and Python — with more coming soon.
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  )
}
