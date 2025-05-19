import { useState, useEffect } from 'react'
import './styles/App.css'
import ItemForm from './components/ItemForm'
import ItemList from './components/ItemList'

// Define item type
interface Item {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch items from the API
  const fetchItems = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/items')
      if (!response.ok) {
        throw new Error(`Error fetching items: ${response.status}`)
      }
      const data = await response.json()
      setItems(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching items:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  // Add a new item
  const addItem = async (name: string, description: string) => {
    try {
      const response = await fetch('/api/items/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
      })
      
      if (!response.ok) {
        throw new Error(`Error creating item: ${response.status}`)
      }
      
      // Refresh the items list
      fetchItems()
    } catch (err) {
      console.error('Error adding item:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  // Delete an item
  const deleteItem = async (id: number) => {
    try {
      const response = await fetch(`/api/items/${id}`, {
        method: 'DELETE',
      })
      
      if (!response.ok) {
        throw new Error(`Error deleting item: ${response.status}`)
      }
      
      // Refresh the items list
      fetchItems()
    } catch (err) {
      console.error('Error deleting item:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  // Fetch items on component mount
  useEffect(() => {
    fetchItems()
  }, [])

  return (
    <div className="container">
      <h1>AI-Friendly Repository</h1>
      
      <div className="card">
        <h2>Add New Item</h2>
        <ItemForm onAddItem={addItem} />
      </div>
      
      <div className="card">
        <h2>Items</h2>
        {loading ? (
          <p>Loading items...</p>
        ) : error ? (
          <p className="error">Error: {error}</p>
        ) : items.length === 0 ? (
          <p>No items found. Add some!</p>
        ) : (
          <ItemList items={items} onDeleteItem={deleteItem} />
        )}
      </div>
    </div>
  )
}

export default App
