# Educational Support RAG Application

An AI-powered educational support system that uses Retrieval-Augmented Generation (RAG) to help students learn from educational materials.

**Website:** [https://arunalla.help/](https://arunalla.help/)

## What is This?

This application helps students by:
- Answering questions based on educational documents
- Supporting multiple languages (English, Sinhala, Tamil)
- Providing real-time chat interactions
- Managing conversation history

## Main Features

### For Students
- 💬 **Chat Interface**: Ask questions and get instant answers
- 📚 **Document-Based Answers**: Responses come from your educational materials
- 🌐 **Multi-Language Support**: Works with English, Sinhala, and Tamil
- 📝 **Chat History**: Review past conversations

### For Administrators
- 🎨 **Admin Panel**: Easy-to-use interface to manage the system
- 📄 **Document Management**: Upload and organize educational materials
- ⚙️ **AI Settings**: Adjust how the AI responds to students

### Technical Features
- 🔐 **Secure Access**: API key protection
- 🚀 **Fast Performance**: Built with modern technology
- 💾 **Data Storage**: Saves chat history and documents
- 🔄 **Real-Time Updates**: Instant message delivery

## Getting Started

### What You Need
- Python 3.8 or newer
- A Google API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation Steps

1. **Download the code**
```bash
git clone <repository-url>
cd educational-support-rag
```

2. **Install required packages**
```bash
pip install -r requirements.txt
```

3. **Set up configuration**
- Copy `.env.example` to `.env`
- Add your Google API key to `.env`

4. **Run the application**
```bash
python main.py
```

5. **Open in browser**
- Go to `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin/ui`

## Configuration

Edit the `.env` file to change settings:

### Basic Settings
```
API_PORT=8000
GOOGLE_API_KEY=your-key-here
```

### Security Settings
```
ADMIN_API_KEY=your-secure-admin-key
ALLOW_ALL_API_KEYS=false
VALID_API_KEYS=key1,key2,key3
```

### Database Settings
```
DATABASE_URL=postgresql://user:password@localhost:5432/database
```

## Adding Educational Documents

### Using the Admin Panel
1. Go to the admin panel
2. Click "Upload Documents"
3. Select PDF files
4. Wait for processing to complete

### Using Command Line
```bash
# Extract text from a PDF
python -m tools.data_feeder.app extract document.pdf

# Download from Google Drive
python -m tools.data_feeder.app download "https://drive.google.com/..."
```

## How to Use the Chat

### For Students
1. Open the website
2. Start typing your question
3. Press Enter or click Send
4. Read the AI's response

### Example Questions
- "What is photosynthesis?"
- "Explain Newton's first law"
- "How do I solve this math problem?"

## Running with Docker

If you prefer using Docker:

```bash
cd deployments/docker
docker-compose up -d
```

Access at `http://localhost:8000`

## API Endpoints

### Student Endpoints
- `POST /init-session` - Start a new chat session
- `POST /chat/sse` - Send a message
- `GET /history` - View chat history

### Admin Endpoints
- `GET /admin/agents` - List AI configurations
- `POST /admin/agents/{name}` - Create new configuration
- `PUT /admin/agents/{name}` - Update configuration

Full API documentation: `http://localhost:8000/docs`

## Supported File Types
- PDF documents
- Text files
- Images (for OCR)

## Language Support
- English
- Sinhala (සිංහල)
- Tamil (தமிழ்)

## Security Features
- API key authentication
- Secure file handling
- Input validation
- Rate limiting

## Troubleshooting

### Application won't start
- Check if Google API key is set in `.env`
- Verify Python version (3.8+)
- Make sure all packages are installed

### Can't upload documents
- Check file size (must be under 100MB)
- Verify file format (PDF, TXT, or images)
- Ensure you have admin access

### Chat not responding
- Check internet connection
- Verify API key is valid
- Look at logs for error messages

## Getting Help

If you encounter issues:
1. Check the error message
2. Review the logs
3. Visit the documentation
4. Contact support

## Contributing

Want to improve this project?
1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Licensed under Apache 2.0 License - see LICENSE file for details.

---

**Built with ❤️ for education**