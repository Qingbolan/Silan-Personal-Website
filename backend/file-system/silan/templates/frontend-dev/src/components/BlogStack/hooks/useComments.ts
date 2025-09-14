import { useState } from 'react';
import { Comment } from '../types/blog';

export const useComments = () => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');

  const handleAddComment = () => {
    if (newComment.trim()) {
      const comment: Comment = {
        id: Date.now(),
        author: 'Current User',
        content: newComment,
        timestamp: new Date().toISOString(),
        likes: 0
      };
      setComments([...comments, comment]);
      setNewComment('');
    }
  };

  return {
    comments,
    newComment,
    setNewComment,
    handleAddComment
  };
}; 