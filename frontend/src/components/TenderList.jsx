"use client"

import { useState, useEffect } from "react"
import { ChevronLeft, ChevronRight, Download, Search } from "lucide-react" // Make sure to install lucide-react


export default function TenderList() {
  const [tenders, setTenders] = useState([])
  const [searchQuery, setSearchQuery] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const itemsPerPage = 5

  //load tenders from backend
  useEffect(() => {
    const fetchTenders = async () => {
      try {
        setLoading(true)
        const res = await fetch("http://127.0.0.1:8000/tenders") // Replace with your actual backend URL
        
        const data = await res.json()
        console.log(data);
        setTenders(data.tenders || []) // Ensure it matches your API structure
      } catch (error) {
        console.error("Failed to fetch tenders:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchTenders()
  }, [])
  // Filter tenders based on search query
  const filteredTenders = Array.isArray(tenders) && tenders.length > 0 ? tenders.filter((tender) => tender?.tender_id?.toLowerCase().includes(searchQuery.toLowerCase())) : []

  // Calculate pagination
  const totalPages = Math.ceil(filteredTenders.length / itemsPerPage)
  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredTenders.slice(indexOfFirstItem, indexOfLastItem)

  // Handle page changes
  const goToNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages))
  }

  const goToPreviousPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1))
  }

  const goToPage = (pageNumber) => {
    setCurrentPage(pageNumber)
  }

  // Reset to first page when search query changes
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1)
  }

  // Generate page numbers
  const getPageNumbers = () => {
    const pageNumbers = []
    const maxPageButtons = 5

    if (totalPages <= maxPageButtons) {
      // Show all pages if total pages are less than max buttons
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i)
      }
    } else {
      // Show a subset of pages with current page in the middle when possible
      let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2))
      let endPage = startPage + maxPageButtons - 1

      if (endPage > totalPages) {
        endPage = totalPages
        startPage = Math.max(1, endPage - maxPageButtons + 1)
      }

      for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i)
      }
    }

    return pageNumbers
  }

  return (
    <div className="tender-list">
      <div className="search-container">
        <div className="search-icon">
          <Search size={16} />
        </div>
        <input
          type="text"
          placeholder="Search tenders..."
          className="search-input"
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

     {/* Loading indicator */}
     {loading ? (
        <p className="loading">Loading tenders...</p> 
      ) : (
      <div className="table-container">
        <table className="tender-table">
          <thead>
            <tr>
              <th>Tender ID</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.length > 0 ? (
              currentItems.map((tender) => (
                <tr key={tender.tender_id}>
                  <td className="tender-id">{tender.tender_id}</td>
                  <td>
                    <a href={tender.s3_url} className="download-link" target="_blank" rel="noopener noreferrer">
                      <span>Download ZIP</span>
                      <Download size={16} />
                    </a>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={2} className="no-results">
                  No tenders found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      )
    }

      {/* Pagination controls */}
      {filteredTenders.length > 0 && (
        <div className="pagination-container">
          <p className="pagination-info">
            Showing {indexOfFirstItem + 1}-{Math.min(indexOfLastItem, filteredTenders.length)} of{" "}
            {filteredTenders.length} tenders
          </p>

          <div className="pagination-controls">
            <button
              className={`pagination-button prev ${currentPage === 1 ? "disabled" : ""}`}
              onClick={goToPreviousPage}
              disabled={currentPage === 1}
            >
              <ChevronLeft size={16} />
              <span className="sr-only">Previous page</span>
            </button>

            <div className="pagination-numbers">
              {getPageNumbers().map((pageNumber) => (
                <button
                  key={pageNumber}
                  className={`pagination-number ${currentPage === pageNumber ? "active" : ""}`}
                  onClick={() => goToPage(pageNumber)}
                >
                  {pageNumber}
                </button>
              ))}
            </div>

            <button
              className={`pagination-button next ${currentPage === totalPages ? "disabled" : ""}`}
              onClick={goToNextPage}
              disabled={currentPage === totalPages}
            >
              <ChevronRight size={16} />
              <span className="sr-only">Next page</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
