import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import { FormField } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import type { Control } from "react-hook-form";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function PromptInput({ control, description, name }: { control: Control<any>, description?: string, name: string }) {
    return (
        <Card className="mb-4">
            <CardHeader>
                <CardDescription className="space-y-4">
                    <Markdown remarkPlugins={[remarkGfm]}>{description}</Markdown>
                </CardDescription>
            </CardHeader>
            <CardContent>
                <FormField control={control}
                    name={name}
                    render={({ field }) => (
                        <Textarea {...field} className="w-full max-h-[500px]"></Textarea>
                    )} />
            </CardContent>
        </Card>
    );
}