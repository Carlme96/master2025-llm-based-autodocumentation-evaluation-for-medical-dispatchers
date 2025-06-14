import { $api } from "@/fetchclient"
import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Form, FormField } from "@/components/ui/form"
import { Accordion, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { AccordionContent } from "@radix-ui/react-accordion"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { queryClient } from "@/main"
import { useNavigate } from "@tanstack/react-router"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import PromptInput from "./PromptInput"
import type { components } from "@/schema/schema"

const formSchema = z.object({
    baseData: z.object({
        appname: z.string(),
        location: z.string(),
        time: z.string(),
        images: z.array(z.string()),
        transcription: z.string(),
    }),
    evaluateBotPrompts: z.object({
        establish_situation_prompt: z.string(),
        summarize_section_prompt: z.string(),
        evaluate_section_prompt: z.string(),
        evaluate_section_not_breathing_prompt: z.string(),
        pairwise_prompt: z.string(),
        extract_advices_prompt: z.string()
    }),
    summaryBotPrompts: z.object({
        describe_case_prompt: z.string(),
        describe_image_prompt: z.string(),
        generate_summary_prompt: z.string(),
        intention_prompt: z.string(),
        transcription_prompt: z.string(),
    })
})

interface PromptDescriptions {
    summaryBotPromptDescriptions: components["schemas"]["SummaryBotPrompts"]
    evaluateBotPromptDescriptions: components["schemas"]["EvaluateBotPrompts"]
}

export default function GenerateReport({ examples, descriptions }: { examples: z.infer<typeof formSchema>, descriptions: PromptDescriptions }) {

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: examples
    })

    const navigate = useNavigate({ from: "/" })

    const { setValue, watch } = form
    const images = watch("baseData.images")

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files) return

        const base64Images = await Promise.all(
            Array.from(files).map((file) => fileToBase64(file))
        )

        setValue("baseData.images", [...images, ...base64Images])
    }

    const fileToBase64 = (file: File): Promise<string> =>
        new Promise((resolve, reject) => {
            const reader = new FileReader()
            reader.onloadend = () => {
                if (typeof reader.result === "string") {
                    resolve(reader.result)
                } else {
                    reject("Error converting file.")
                }
            }
            reader.readAsDataURL(file)
        })

    const handleRemoveImage = (indexToRemove: number) => {
        const updatedImages = images.filter((_, index) => index !== indexToRemove)
        setValue("baseData.images", updatedImages)
    }

    const { mutate } = $api.useMutation("post", "/report/report-generate", {
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["get", "/report/get_reports"] })
            navigate({ to: data.id })
        },
        onError: (error) => {
            console.error(error)
        }
    })

    const onSubmit = (data: z.infer<typeof formSchema>) => {
        const evaluateBotPrompts = data.evaluateBotPrompts
        const baseData = data.baseData
        const summaryBotPrompts = data.summaryBotPrompts

        const payload = {
            evaluateBotPrompts,
            summaryBotPrompts,
            baseData: {
                ...baseData,
                transcription: JSON.parse(data.baseData.transcription)
            }
        }
        mutate({ body: payload })
    }

    return (
        <div className="m-10">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)}>
                    <Card>
                        <CardHeader>
                            <CardTitle>Generate Report</CardTitle>
                            <CardDescription>
                                Fill in the details below to generate a report.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <FormField control={form.control}
                                    name="baseData.appname"
                                    render={({ field }) => (
                                        <div className="grid w-full max-w-sm items-center gap-1.5">
                                            <Label className="text-sm font-bold" htmlFor="baseData.appname">App Name</Label>
                                            <Input {...field} placeholder="App Name" />
                                        </div>
                                    )} />
                                <FormField control={form.control}
                                    name="baseData.location"
                                    render={({ field }) => (
                                        <div className="grid w-full max-w-sm items-center gap-1.5">
                                            <Label className="text-sm font-bold" htmlFor="baseData.location">Location</Label>
                                            <Input {...field} placeholder="Location" />
                                        </div>
                                    )} />
                                <FormField control={form.control}
                                    name="baseData.time"
                                    render={({ field }) => (
                                        <div className="grid w-full max-w-sm items-center gap-1.5">
                                            <Label className="text-sm font-bold" htmlFor="baseData.time">Time</Label>
                                            <Input {...field} placeholder="Time" />
                                        </div>
                                    )} />
                                <div className="grid w-full max-w-sm items-center gap-1.5">
                                    <Label className="text-sm font-bold" htmlFor="images">Upload Image</Label>
                                    <Input type="file" accept="image/*" name="images" multiple onChange={handleImageUpload} />
                                </div>
                            </div>

                            <Accordion type="single" collapsible >
                                <AccordionItem value="item-0">
                                    <AccordionTrigger>Images</AccordionTrigger>
                                    <AccordionContent>
                                        {images.length === 0 && <p className="text-sm pb-4 pl-4 text-orange-500">No images uploaded.</p>}
                                        {images.length > 0 && <div className="grid grid-cols-2 gap-4">
                                            {images.map((image, index) => (
                                                <Card key={index} className="p-4 group">
                                                    <img src={image} className="max-h-96 object-scale-down" alt={`Image ${index}`} />
                                                    <Button variant="default" className="absolute hidden group-hover:block bg-red-500 m-2" onClick={() => handleRemoveImage(index)}>X</Button>

                                                </Card>
                                            ))}
                                        </div>}
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-1">
                                    <AccordionTrigger>Transcription</AccordionTrigger>
                                    <AccordionContent>
                                        <Card className="">
                                            <CardHeader>
                                                <CardTitle>The transcription of the conversation.</CardTitle>
                                                <CardDescription>
                                                    Format:
                                                    <p className="text-sm">
                                                        [
                                                        <br />
                                                        "0, example text",
                                                        <br />
                                                        "1, example text",
                                                        <br />
                                                        ...
                                                        <br />
                                                        "0, example text"
                                                        <br />
                                                        ]
                                                        <br />
                                                        <br />
                                                        Where 0 is the dispatcher and 1 is the caller.
                                                        <br />
                                                        Remember to not add a comma at the end of the last element.
                                                    </p>
                                                </CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <FormField control={form.control}
                                                    name="baseData.transcription"
                                                    render={({ field }) => (
                                                        <Textarea {...field} placeholder="Transcription" className="w-full max-h-[500px]" />
                                                    )} />
                                            </CardContent>
                                        </Card>
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                    <Card className="mt-4">
                        <CardHeader>
                            <CardTitle>Evaluate bot prompts</CardTitle>
                            <CardDescription>
                                You can change the default prompts for the evaluation bot here.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Accordion type="single" collapsible >
                                <AccordionItem value="item-1">
                                    <AccordionTrigger>Summarize Section Prompt</AccordionTrigger>
                                    <AccordionContent >
                                        <PromptInput control={form.control} name="evaluateBotPrompts.summarize_section_prompt" description={descriptions.evaluateBotPromptDescriptions.summarize_section_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-2">
                                    <AccordionTrigger>Establish Situation Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="evaluateBotPrompts.establish_situation_prompt" description={descriptions.evaluateBotPromptDescriptions.establish_situation_prompt} />

                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-3">
                                    <AccordionTrigger>Evaluate Section Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="evaluateBotPrompts.evaluate_section_prompt" description={descriptions.evaluateBotPromptDescriptions.evaluate_section_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-4">
                                    <AccordionTrigger>Evaluate Section Not Breathing Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="evaluateBotPrompts.evaluate_section_not_breathing_prompt" description={descriptions.evaluateBotPromptDescriptions.evaluate_section_not_breathing_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-5">
                                    <AccordionTrigger>Pairwise Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="evaluateBotPrompts.pairwise_prompt" description={descriptions.evaluateBotPromptDescriptions.pairwise_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-6">
                                    <AccordionTrigger>Extract Advices Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="evaluateBotPrompts.extract_advices_prompt" description={descriptions.evaluateBotPromptDescriptions.extract_advices_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                    <Card className="mt-4">
                        <CardHeader>
                            <CardTitle>Summary bot prompt</CardTitle>
                        </CardHeader>
                        <CardContent>

                            <Accordion type="single" collapsible >
                                <AccordionItem value="item-2">
                                    <AccordionTrigger>Describe Case Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="summaryBotPrompts.describe_case_prompt" description={descriptions.summaryBotPromptDescriptions.describe_case_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-3">
                                    <AccordionTrigger>Describe Image Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="summaryBotPrompts.describe_image_prompt" description={descriptions.summaryBotPromptDescriptions.describe_image_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-4">
                                    <AccordionTrigger>Generate Summary Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="summaryBotPrompts.generate_summary_prompt" description={descriptions.summaryBotPromptDescriptions.generate_summary_prompt} />
                                    </AccordionContent>
                                </AccordionItem>

                                <AccordionItem value="item-5">
                                    <AccordionTrigger>Intention Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="summaryBotPrompts.intention_prompt" description={descriptions.summaryBotPromptDescriptions.intention_prompt} />
                                    </AccordionContent>
                                </AccordionItem>

                                <AccordionItem value="item-6">
                                    <AccordionTrigger>Transcription Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <PromptInput control={form.control} name="summaryBotPrompts.transcription_prompt" description={descriptions.summaryBotPromptDescriptions.transcription_prompt} />
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                    <Button type="submit" className="mt-4">Generate</Button>
                </form>
            </Form>
        </div>)
}