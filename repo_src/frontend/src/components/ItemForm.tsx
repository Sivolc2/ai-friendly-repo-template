import { useState, FormEvent } from 'react'

interface ItemFormProps {
  onAddItem: (name: string, description: string) => Promise<void>
}

function ItemForm({ onAddItem }: ItemFormProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    if (!name.trim()) {
      alert('Name is required')
      return
    }
    
    try {
      setIsSubmitting(true)
      await onAddItem(name, description)
      
      // Reset form after successful submission
      setName('')
      setDescription('')
    } catch (error) {
      console.error('Error in form submission:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={isSubmitting}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="description">Description:</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isSubmitting}
        />
      </div>
      
      <button 
        type="submit" 
        className="button-primary"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Adding...' : 'Add Item'}
      </button>
    </form>
  )
}

export default ItemForm 