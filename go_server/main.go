package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
)

func main() {
	http.HandleFunc("/upload-face", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		// Retrieve file from the request
		file, fileHeader, err := r.FormFile("file")
		if err != nil {
			http.Error(w, "No file provided", http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Prepare to send file to the Python microservice
		bodyBuf := &bytes.Buffer{}
		writer := multipart.NewWriter(bodyBuf)
		part, err := writer.CreateFormFile("file", fileHeader.Filename)
		if err != nil {
			http.Error(w, "Failed to create form file", http.StatusInternalServerError)
			return
		}
		io.Copy(part, file)
		writer.Close()

		// Send POST request to the Python recognition service
		req, err := http.NewRequest("POST", "https://bug-free-palm-tree-4xjq6r9j9jc7wvj-5000.app.github.dev/recognize-face", bodyBuf)
		if err != nil {
			http.Error(w, "Failed to create request", http.StatusInternalServerError)
			return
		}
		req.Header.Set("Content-Type", writer.FormDataContentType())

		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to call recognition service err: %v", err), http.StatusInternalServerError)
			return
		}
		defer resp.Body.Close()

		// Return Python service response back to the caller
		w.Header().Set("Content-Type", "application/json")
		io.Copy(w, resp.Body)
	})

	port := "8080"
	fmt.Printf("Go service is running on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
