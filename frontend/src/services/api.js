const BASE_URL = import.meta.env.VITE_API_URL

async function request(method, path, body = null) {
  const headers = {
    'Content-Type': 'application/json',
  }

  const options = { method, headers }
  if (body) {
    options.body = JSON.stringify(body)
  }

  return fetch(`${BASE_URL}${path}`, options)
}

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  put: (path, body) => request('PUT', path, body),
  delete: (path) => request('DELETE', path),
}
