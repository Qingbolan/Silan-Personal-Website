import { useState } from 'react';
import { Comment } from '../types/blog';

export const useComments = () => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');

  const handleAddComment = () => {
    if (newComment.trim()) {
      const comment: Comment = {
        id: Date.now().toString(),
        blog_post_id: '',
        author_name: 'Current User',
        content: newComment,
        created_at: new Date().toISOString()
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