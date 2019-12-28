import React, { Component } from 'react'

import Dropzone from 'react-dropzone'

class ImgDragAndDrop extends Component {

    onDrop = (acceptedFiles) => {
        console.log(acceptedFiles);
      }
    render() {
        return (
            <div>
                <h1>Convert Image</h1>
                <Dropzone onDrop={this.onDrop}>
                    {({getRootProps, getInputProps}) => (
                        <section>
                        <div {...getRootProps()}>
                            <input {...getInputProps()} />
                            <p>Drop some files here, or click to select files</p>
                        </div>
                        </section>
                    )}
                </Dropzone>
            </div>
        )
    }
}

export default ImgDragAndDrop;