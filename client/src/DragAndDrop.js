import React, { Component } from 'react'
import Dropzone from 'react-dropzone'
import { Form, Button } from 'semantic-ui-react'

class ImgDragAndDrop extends Component {
    constructor(props) {
        super(props);
        this.state = {
            images: []
        }
    }

    onDrop = (acceptedFiles) => {
        this.state.images.push(acceptedFiles);
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
                <Form>
                    <Form.Field>
                        <Button onClick={async () => {
                            const { images } = this.state; 
                            const response = await fetch('/extract_text', {
                                method: 'POST',
                                body: images[0]
                            });

                            console.log(response);
                        }}>submit</Button>
                    </Form.Field>
                    <Form.Field>
                        <Button onClick={async () => {
                            const response = await fetch('/download_file');

                            console.log(response);
                        }}>download</Button>
                    </Form.Field>
                </Form>
            </div>
        )
    }
}

export default ImgDragAndDrop;