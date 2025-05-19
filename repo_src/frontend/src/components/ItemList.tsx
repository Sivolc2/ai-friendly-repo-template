import React from 'react'

interface Item {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

interface ItemListProps {
  items: Item[]
  onDeleteItem: (id: number) => Promise<void>
}

function ItemList({ items, onDeleteItem }: ItemListProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      await onDeleteItem(id)
    }
  }

  return (
    <ul className="item-list">
      {items.map(item => (
        <li key={item.id} className="item">
          <div className="item-content">
            <div className="item-name">{item.name}</div>
            {item.description && (
              <div className="item-description">{item.description}</div>
            )}
            <div className="item-date">
              Created: {formatDate(item.created_at)}
            </div>
          </div>
          <button 
            onClick={() => handleDelete(item.id)}
            className="item-delete"
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  )
}

export default ItemList 