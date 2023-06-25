"use client";
import React, { useState, useEffect} from "react";
import { Button, Stack, Form, Spinner  } from "react-bootstrap";
import { ToastContainer, toast } from "react-toastify";
import Dropzone from 'react-dropzone';

export default function ConfigSideNav() {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [isUploading, setIsUploading] = useState(null);
  const [ingestedFiles, setIngestedFiles] = useState([])

  useEffect(() => {
    const fetchIngestedFiles = async() =>{
      const res = await fetch("http://localhost:5555/get_ingested_files", {
        method: "GET",
      });
      const data = await res.json()
      setIngestedFiles(data["ingested_files"].sort(function(a, b) {
        return a.toLowerCase().localeCompare(b.toLowerCase());
      }));
    }
    fetchIngestedFiles().then(() => {});
  }, []); // Empty dependency array ensures this runs once on component mount

  const handleFetchIngestedFiles = async() =>{
    const res = await fetch("http://localhost:5555/get_ingested_files", {
      method: "GET",
    });
    const data = await res.json();
    setIngestedFiles(data["ingested_files"].sort(function(a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    }));
  }

  const handleFileChangeDrop = (files) => {
    setSelectedFiles(files)
  };

  const handleUpload = async () => {
    setIsUploading(true)
    try {
      const formData = new FormData();

      for (let file of selectedFiles) {
        // console.log(`selectedFiles file ${file.name}`)
        formData.append('documents', file);
      }

      const res = await fetch("http://localhost:5555/upload_files", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        console.log("Error Uploading document");
		response.text().then(text => {toast.error("Error Uploading document."+text);})
        setSelectedFiles(null)
        setIsUploading(false)
      } else {
        const data = await res.json();
        console.log(data);
        toast.success("Document Upload Successful");
        setSelectedFiles(null)
        setIsUploading(false)
      }
    } catch (error) {
      console.log("error");
      toast.error("Error Uploading document");
      setSelectedFiles(null)
      setIsUploading(false)
    }

    await handleFetchIngestedFiles()
  };

  const handlePurge = async () => {
    await fetch("http://localhost:5555/purge", {
      method: "GET",
    });
    await handleFetchIngestedFiles()
  }

  function renderIngestedFiles() {
    if (ingestedFiles.length === 0) {
      return <div></div>
    }
    return (
        <div>
          <hr/>
          <h5>Ingested files</h5>
          <ul>
            {ingestedFiles.map((item, index) =>
                <li key={index}>{item}</li>
            )}
          </ul>
          <Button onClick={(e) => handlePurge()}>
            Remove All Ingested Files
          </Button>
        </div>
    );
  }

  function renderSelectedFiles() {
    if (selectedFiles === null || selectedFiles.length === 0) {
      return <div></div>
    }
    return (
        <div>
          <ul>
            {selectedFiles.map((item, index) =>
                <li key={index}>{item.name}</li>
            )}
          </ul>
        </div>
    );
  }

  return (
    <>
      <div className="mx-4 mt-3">
        <Dropzone onDrop={acceptedFiles => {handleFileChangeDrop(acceptedFiles)} }>
          {({getRootProps, getInputProps, isDragActive}) => (
              <section>
                <div {...getRootProps({style: { backgroundColor: isDragActive ? 'lightgreen' : 'lightgray', padding: '20px', margin: '0 0 20px 0'}})}>
                  <input {...getInputProps()} />
                  {
                    selectedFiles == null ?
                          <p>Drag 'n' drop some files here. <br/>Or click to select files to ingest.</p> :<div>
                          <p>File(s) selected:</p>
                          {renderSelectedFiles()}
                        </div>
                  }
                </div>
              </section>
          )}
        </Dropzone>
        { isUploading &&
          <div className="d-flex justify-content-center"><Spinner animation="border" />
            <span className="ms-3">uploading</span>
          </div>
        }
        {!isUploading && selectedFiles != null &&
            <Button onClick={(e) => handleUpload()}>
            Ingest
            </Button>
        }
      </div>

      <div className="mx-4 mt-3 fw-light">
        { renderIngestedFiles(ingestedFiles)}
      </div>
    </>
  );
}
