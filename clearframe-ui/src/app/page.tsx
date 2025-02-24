"use client";
import { useState } from "react";
import { FileUploader } from "react-drag-drop-files";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  // State for handling files
  const [files, setFiles] = useState<File[]>([]);
  const [uploaded, setUploaded] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processedImages, setProcessedImages] = useState<string[]>([]);
  const fileTypes = ["JPG", "PNG", "WEBP"];

  // Handle file selection
  const handleChange = (file: File) => {
    setFiles((prevFiles) => [...prevFiles, file]);
  };

  // Upload and process images
  const handleUpload = async () => {
    if (files.length === 0) {
      alert("No files selected!");
      return;
    }

    setProcessing(true);
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch(`${API_URL}/api/batch-process/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setUploaded(true);
        fetchProcessedImages();
      } else {
        alert("Upload failed!");
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setProcessing(false);
    }
  };

  // Fetch processed images
  const fetchProcessedImages = async () => {
    try {
      const response = await fetch(`${API_URL}/api/get-processed/`);
      const data = await response.json();
      setProcessedImages(data.images || []);
    } catch (error) {
      console.error("Error fetching processed images:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">ClearFrame Image Processing</h1>

      <Card className="w-full max-w-lg p-6 bg-white shadow-lg">
        <CardContent>
          {/* File Upload Component */}
          <FileUploader
            handleChange={handleChange}
            name="file"
            types={fileTypes}
            multiple
            {...(false ? { error: true } : {})} // ✅ Fixes `error=false` issue
          />

          {/* Display Selected Files */}
          <div className="mt-4 flex flex-wrap gap-4">
            {files.map((file, index) => (
              <div key={index} className="p-2 bg-gray-200 rounded-lg">
                {file.name}
              </div>
            ))}
          </div>

          {/* Process Button */}
          <Button className="mt-4 w-full" onClick={handleUpload} disabled={processing}>
            {processing ? "Processing..." : "Process Images"}
          </Button>

          {/* Display Processed Images */}
          {uploaded && processedImages.length > 0 && (
            <div className="mt-6">
              <h2 className="text-xl font-bold">Processed Images:</h2>
              <div className="flex flex-wrap gap-4">
                {processedImages.map((img, idx) => (
                  <img
                    key={idx}
                    src={`${API_URL}/api/get-processed/${img}`}
                    alt="Processed"
                    className="w-32 h-auto rounded-lg"
                  />
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
