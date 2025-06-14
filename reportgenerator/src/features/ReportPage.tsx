import { Button, buttonVariants } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer"
import { NavigationMenu, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger, NavigationMenuContent } from "@/components/ui/navigation-menu"
import { $api } from "@/fetchclient"
import type { components } from "@/schema/schema"
import { useMatch, useParams } from "@tanstack/react-router"
import { useMemo, useState } from "react"
import Markdown from "react-markdown"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm'
import { Copy } from "lucide-react"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"



function BaseData({ data }: { data: components["schemas"]["BaseData"] }) {

    return (
        <div className="flex gap-4 justify-stretch items-stretch w-full">
            <Card className="w-150">
                <CardHeader>
                    <CardTitle>Report info</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="font-bold">Location: <span className="font-normal">{data.location}</span></div>
                    <div className="font-bold">App name: <span className="font-normal">{data.appname}</span></div>
                    <div className="font-bold">Time: <span className="font-normal">{data.time}</span></div>
                </CardContent>
            </Card>
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>Transcription</CardTitle>
                </CardHeader>
                <CardContent className="h-96">
                    <div className="relative group" >
                        <Button variant="outline" className="absolute top-2 right-2 hidden group-hover:block" onClick={() => navigator.clipboard.writeText(data.transcription as unknown as string)}><Copy /></Button>
                        <SyntaxHighlighter
                            language="json"
                            style={vscDarkPlus}
                            lineProps={{ style: { wordBreak: 'break-all', whiteSpace: 'pre-wrap' } }}
                            wrapLines={true}
                            customStyle={{ maxHeight: "24rem", overflowY: "scroll" }}

                        >{JSON.stringify(data.transcription, null, 2)}</SyntaxHighlighter>
                    </div>
                </CardContent>
            </Card>
        </div>

    )

}


function Prompts({ prompt, title }: { prompt: string, title: string }) {

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent className="h-96">
                <div className="relative group" >
                    <Button variant="outline" className="absolute top-2 right-2 hidden group-hover:block" onClick={() => navigator.clipboard.writeText(prompt)}><Copy /></Button>
                    <SyntaxHighlighter
                        language="markdown"
                        style={vscDarkPlus}
                        lineProps={{ style: { wordBreak: 'break-all', whiteSpace: 'pre-wrap' } }}
                        wrapLines={true}
                        customStyle={{ maxHeight: "24rem", overflowY: "scroll" }}


                    >{prompt}</SyntaxHighlighter>
                </div>
            </CardContent>
        </Card>

    )

}

type Pages = "base_data" | { page: "summary_bot_prompts", subPage: string } | { page: "evaluate_bot_prompts", subPage: string }

function GetRuninfo({ reportId }: { reportId: string }) {
    const [page, setPage] = useState<Pages>("base_data")

    const { data } = $api.useQuery("get", "/report/get_report/{id}", {
        params: {
            path: { id: reportId },
        }
    })

    const pages = useMemo(() => {
        return {
            summary_bot_prompts: Object.keys(data?.state.summaryBotPrompts || []),
            evaluate_bot_prompts: Object.keys(data?.state.evaluateBotPrompts || []),
        }
    }, [data])

    return (
        <Drawer>
            <DrawerTrigger className={buttonVariants({ variant: "outline" })}>Details</DrawerTrigger>
            <DrawerContent className="p-4 pt-0">
                <DrawerHeader>
                    <DrawerTitle>Run info</DrawerTitle>
                    <DrawerDescription><NavigationMenu>
                        <NavigationMenuList>
                            <NavigationMenuItem>
                                <NavigationMenuLink onClick={() => setPage("base_data")} className={`cursor-pointer ${page === "base_data" ? "border" : ""}`}>
                                    Base Data
                                </NavigationMenuLink>
                            </NavigationMenuItem>
                            <NavigationMenuItem>
                                <NavigationMenuTrigger className={`cursor-pointer ${page != "base_data" && page.page === "summary_bot_prompts" ? "border" : ""}`}>
                                    Summary Bot Prompts
                                </NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">

                                        {pages.summary_bot_prompts.map((item) => (
                                            <li className="row-span-3 list-none">
                                                <NavigationMenuLink key={item} onClick={() => setPage({ page: "summary_bot_prompts", subPage: item })} className={`cursor-pointer ${page !== "base_data" && page.page === "summary_bot_prompts" && page.subPage === item ? "border" : ""}`}>
                                                    {item}
                                                </NavigationMenuLink>
                                            </li>
                                        ))}
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>
                            <NavigationMenuItem>
                                <NavigationMenuTrigger className={`cursor-pointer ${page != "base_data" && page.page === "evaluate_bot_prompts" ? "border" : ""}`}>
                                    Evaluate Bot Prompts
                                </NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">

                                        {pages.evaluate_bot_prompts.map((item) => (
                                            <li className="row-span-3 list-none">
                                                <NavigationMenuLink key={item} onClick={() => setPage({ page: "evaluate_bot_prompts", subPage: item })} className={`cursor-pointer ${page !== "base_data" && page.page === "evaluate_bot_prompts" && page.subPage === item ? "border" : ""}`}>
                                                    {item}
                                                </NavigationMenuLink>
                                            </li>
                                        ))}
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>
                        </NavigationMenuList>
                    </NavigationMenu></DrawerDescription>
                </DrawerHeader>

                {page === "base_data" && data?.state.baseDataSummaryBot && <BaseData data={data?.state.baseDataSummaryBot} />}
                {page.page === "summary_bot_prompts" && data?.state.summaryBotPrompts && <Prompts prompt={data?.state.summaryBotPrompts[page.subPage]} title={page.subPage} />}
                {page.page === "evaluate_bot_prompts" && data?.state.evaluateBotPrompts && <Prompts prompt={data?.state.evaluateBotPrompts[page.subPage]} title={page.subPage} />}
            </DrawerContent>
        </Drawer>
    )

}

type EvaluationReport = {
    normal?: string | undefined | null
    detailed?: string | undefined | null
}

function EvaluationResult({ evaluationReports }: { evaluationReports: EvaluationReport[] }) {
    const [showDetailed, setShowDetailed] = useState(false)

    if (!evaluationReports) return null

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex justify-between">
                    <div>Evaluation Result</div>
                    <div className="flex items-center">
                        <Label htmlFor="showDetailed" className="mr-2">Show detailed</Label>
                        <Switch id="showDetailed" checked={showDetailed} onCheckedChange={() => setShowDetailed(!showDetailed)} />
                    </div>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {!showDetailed && evaluationReports.map((report) => <Markdown remarkPlugins={[remarkGfm]}>{report.normal}</Markdown>)}
                {showDetailed && evaluationReports.map((report) => <Markdown remarkPlugins={[remarkGfm]}>{report.detailed}</Markdown>)}
            </CardContent>
        </Card>
    )
}

export default function ReportPage() {

    const { reportId } = useParams({ from: "/$reportId" })

    const { data } = $api.useQuery("get", "/report/get_report/{id}", {
        params: {
            path: { id: reportId },
        }
    }, {
        refetchInterval: 1000,
    })

    const evaluationReports = useMemo(() => {
        if (!data?.state.evaluateBotState.sections) return []
        const sections = data.state.evaluateBotState.sections
        return sections.map((section) => {
            return {
                normal: section.result,
                detailed: section.resultDetailed,
            }
        })
    }, [data])


    return (
        <div className="space-y-4">
            <h1 className="text-2xl font-bold mb-8">Report</h1>
            <div className="flex gap-4 items-stretch justify-between">
                <Card className="w-full">
                    <CardHeader>
                        <CardTitle className="flex justify-between items-center -mt-2"><span>Run Info</span> <GetRuninfo reportId={reportId} /></CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 ml-2">
                        <div className="font-bold">Report ID: <span className="font-normal">{reportId}</span></div>
                        <div className="font-bold">Job started: <span className="font-normal">{data?.created_at && new Date(data.created_at).toLocaleString("nb-no")}</span></div>
                        <div className="font-bold">Job finished: <span className="font-normal">{data?.finished ? "Finished" : "Not finished"}</span></div>
                        {!data?.finished && <p className="text-red-500 text-sm">The report is still being generated. Or it did not finish. Try again later.</p>}
                    </CardContent>
                </Card>
                <Card className="w-full">
                    <CardHeader>
                        <CardTitle>Report info</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 ml-2">
                        <div className="font-bold">Location: <span className="font-normal">{data?.state.baseDataEvaluateBot.location}</span></div>
                        <div className="font-bold">App name: <span className="font-normal">{data?.state.baseDataEvaluateBot.appname}</span></div>
                        <div className="font-bold">Time: <span className="font-normal">{data?.state.baseDataEvaluateBot.time}</span></div>
                    </CardContent>
                </Card>
            </div>
            {data?.state.summaryBotState.summaryBotResult && <Card>
                <CardHeader>
                    <CardTitle>Report</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <Markdown remarkPlugins={[remarkGfm]}>{data?.state.summaryBotState.summaryBotResult}</Markdown>
                    {data?.state.imageDescriptions.length > 0 && <><h1>Images</h1><div className="grid grid-cols-3 gap-4">

                        {data?.state.imageDescriptions.map((image, idx) => {
                            return (
                                <Card key={idx} className="w-full ">

                                    <CardContent className="flex flex-col items-center gap-4">

                                        <img key={image.image} src={image.image} alt="Screenshot" className="max-h-96 rounded-lg" />
                                        <CardDescription>
                                            {image.description}
                                        </CardDescription>
                                    </CardContent>
                                </Card>
                            )
                        })}
                    </div></>}

                </CardContent>
            </Card>}
            <EvaluationResult evaluationReports={evaluationReports} />
        </div>
    )
}