import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './MyStacks.css'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function MyStacks() {
  const [stacks, setStacks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchStacks()
  }, [])

  const fetchStacks = async () => {
    try {
      const response = await axios.get(`${API_URL}/stacks/`)
      setStacks(response.data)
    } catch (err) {
      setError('Failed to load stacks')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const deleteStack = async (stackId) => {
    if (!confirm('Are you sure you want to delete this stack?')) {
      return
    }

    try {
      await axios.delete(`${API_URL}/stacks/${stackId}/`)
      setStacks(stacks.filter(s => s.id !== stackId))
    } catch (err) {
      alert('Failed to delete stack')
      console.error(err)
    }
  }

  if (loading) {
    return <div className="page-container loading">Loading your stacks...</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>My Saved Stacks</h1>
        <button className="primary-btn" onClick={() => navigate('/dashboard')}>
          + Create New Stack
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {stacks.length === 0 ? (
        <div className="empty-state">
          <p>You haven't saved any stacks yet.</p>
          <button onClick={() => navigate('/dashboard')}>Create Your First Stack</button>
        </div>
      ) : (
        <div className="stacks-grid">
          {stacks.map(stack => (
            <div key={stack.id} className="stack-card">
              <div className="stack-header">
                <h3>{stack.stack_name}</h3>
                {stack.is_public && <span className="public-badge">Public</span>}
              </div>

              {stack.description && (
                <p className="stack-description">{stack.description}</p>
              )}

              <div className="stack-meta">
                <span>Created: {new Date(stack.created_at).toLocaleDateString()}</span>
                <span>Updated: {new Date(stack.updated_at).toLocaleDateString()}</span>
              </div>

              <div className="stack-actions">
                <button className="load-btn">Load</button>
                <button className="edit-btn">Edit</button>
                <button
                  className="delete-btn"
                  onClick={() => deleteStack(stack.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyStacks
