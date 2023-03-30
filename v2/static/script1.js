new Vue({
  el: '#app',
  data: () => {
    return {
      signUp: false
    }
  }
})

document.addEventListener('DOMContentLoaded', () => {
  // Fetch categories and tags, and populate the filter dropdown menus
  fetchCategories();
  fetchTags();

  // Add event listeners to filter elements
  document.getElementById('category-filter').addEventListener('change', filterScams);
  document.getElementById('tag-filter').addEventListener('change', filterScams);
  document.getElementById('latest-filter').addEventListener('click', filterScams);

  function fetchCategories() {
    // Get the current category from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentCategory = urlParams.get('category') || '';

    fetch('/?get_categories=1')
      .then(response => response.json())
      .then(categories => {
        const categoryFilter = document.getElementById('category-filter');
        categories.forEach(category => {
          const option = document.createElement('option');
          option.value = category;
          option.textContent = category;
          // Set the selected option if it matches the current category
          if (category === currentCategory) {
            option.selected = true;
          }
          categoryFilter.appendChild(option);
        });
      });
  }

  function fetchTags() {
    // Get the current tag from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentTagId = urlParams.get('tag_id') || '';

    fetch('/tags')
      .then(response => response.json())
      .then(tags => {
        const tagFilter = document.getElementById('tag-filter');
        tags.forEach(tag => {
          const option = document.createElement('option');
          option.value = tag.id;
          option.textContent = tag.name;
          // Set the selected option if it matches the current tag
          if (tag.id.toString() === currentTagId) {
            option.selected = true;
          }
          tagFilter.appendChild(option);
        });
      });
  }


  function filterScams() {
    // Get filter values
    const categoryFilterValue = document.getElementById('category-filter').value;
    const tagFilterValue = document.getElementById('tag-filter').value;

    // Build query parameters
    const queryParams = new URLSearchParams();

    if (categoryFilterValue) {
      queryParams.append('category', categoryFilterValue);
    }

    if (tagFilterValue) {
      queryParams.append('tag_id', tagFilterValue);
    }

    // Redirect to the updated URL
    window.location.href = '/?' + queryParams.toString();
  }
});


const signInButtonDropdown = document.getElementById('signin-button');
const signUpButtonDropdown = document.getElementById('signup-button');
const loginContainer = document.getElementById('app');
const container1 = document.querySelector('.container1');

signInButtonDropdown.addEventListener('click', () => {
  loginContainer.classList.add('show-login');
  container1.classList.remove('sign-up-active');
  container1.classList.add('sign-in-active');
});

signUpButtonDropdown.addEventListener('click', () => {
  loginContainer.classList.add('show-login');
  container1.classList.add('sign-up-active');
  container1.classList.remove('sign-in-active');
});

window.addEventListener('click', (event) => {
  if (event.target === loginContainer) {
    loginContainer.classList.remove('show-login');
  }
});

document.addEventListener('DOMContentLoaded', function() {
  const postItems = document.querySelectorAll('.col-s-4');
  
  postItems.forEach(function(postItem) {
    postItem.addEventListener('click', function() {
      const postId = this.getAttribute('data-post-id');
      window.location.href = `/view_post/${postId}`;
    });
  });
});


$(function () {
  $(".sidebar-link").click(function () {
    $(".sidebar-link").removeClass("is-active");
    $(this).addClass("is-active");
  });

  $(window).resize(function () {
    if ($(window).width() > 1090) {
      $(".sidebar").removeClass("collapse");
    } else {
      $(".sidebar").addClass("collapse");
    }
  }).resize();

  $(".video-stream source").attr("src", source);

  $(".logo, .logo-expand, .discover").on("click", function (e) {
    $(".main-container").removeClass("show");
    $(".main-container").scrollTop(0);
  });

  $(".trending, .video").on("click", function (e) {
    $(".main-container").addClass("show");
    $(".main-container").scrollTop(0);
    $(".sidebar-link").removeClass("is-active");
    $(".trending").addClass("is-active");
  });

  $(".video").click(function () {
    var source = $(this).find("source").attr("src");
    var title = $(this).find(".video-name").text();
    var person = $(this).find(".video-by").text();
    var img = $(this).find(".author-img").attr("src");
    $(".video-stream video").stop();
    $(".video-stream source").attr("src", source);
    $(".video-stream video").load();
    $(".video-p-title").text(title);
    $(".video-p-name").text(person);
    $(".video-detail .author-img").attr("src", img);
  });
});

angular.module('blogApp', [])
  .controller('BlogController', ['$http', '$scope', function ($http, $scope) {    var blog = this;
    blog.posts = [];

    // Fetch the list of posts from the server
    $http.get('/all_posts').then(function (response) {
        blog.posts = response.data;
    });

    // Fetch the individual post data
    var postId = window.location.pathname.split('/').pop();
    $http.get('/post/' + postId).then(function (response) {
      blog.post = response.data;
      blog.post.comments = response.data.comments;
    });

    // Add the likePost function to the controller
    blog.likePost = function() {
      const likeUrl = document.getElementById("like-button").getAttribute("data-url");
      fetch(likeUrl, {
        method: "POST"
      })
        .then(function(response) {
          if (!response.ok) {
            throw Error(response.statusText);
          }
          return response.json();
        })
        .then(function(data) {
          document.querySelector(".like-count").textContent = data.likes;
        })
        .catch(function(error) {
          console.log(error);
        });
    };
    

    blog.isSelected = function (tab) {
      return blog.selectedTab === tab;
    };

    blog.selectTab = function (tab) {
      blog.selectedTab = tab;
    };

    // Set the default selected tab
    blog.selectTab('blog');

    blog.addComment = function (postId) {
      var postIndex = blog.posts.findIndex(function (post) {
        return post.id === postId;
      });
    
      var post = blog.posts[postIndex];
      var body = document.getElementById('comment-body-' + postId).value;
      var author = document.getElementById('comment-author-' + postId).value;

      var data = {
        'body': body,
        'author': author
      };

      // Set the Content-Type header
      $http.post('/post/' + postId + '/comment', data, {
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function (response) {
        post.comments.push({
          'body': response.data.body,
          'author': response.data.author
        });
        document.getElementById('comment-form-' + postId).reset();
      }).catch(function (error) {
        console.log(error);
      });
    };
}]);

  function likePost(postId, post) {
    fetch('/post/' + postId + '/like', {
      method: 'POST'
    })
      .then(function (response) {
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
      })
      .then(function (data) {
        post.likes = data.likes;
      })
      .catch(function (error) {
        console.log(error);
      });
  }
  

function addPost() {
  var title = document.getElementById('title').value;
  var body = document.getElementById('body').value;
  var image = document.getElementById('image').value;
  var author = document.getElementById('author').value;
  var data = {
    'title': title,
    'body': body,
    'image': image,
    'author': author
  };
  fetch('/post/new', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(function (response) {
      if (!response.ok) {
        throw Error(response.statusText);
      }
      return response;
    })
    .then(function (response) {
      window.location.href = '/';
    })
    .catch(function (error) {
      console.log(error);
    });
}

function previousPage(currentPage) {
  if (currentPage > 1) {
    window.location.href = '/page/' + (currentPage - 1);
  }
}

function nextPage(currentPage, totalPages) {
  if (currentPage < totalPages) {
    window.location.href = '/page/' + (currentPage + 1);
  }
}

document.getElementById("like-button").addEventListener("click", function(event) {
  event.preventDefault(); // Prevent form submission

  const likeUrl = this.closest("form").action;
  fetch(likeUrl, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(function(response) {
      if (!response.ok) {
        throw Error(response.statusText);
      }
      return response.json();
    })
    .then(function(data) {
      if (data.result === "success") {
        document.querySelector(".like-count").textContent = data.likes;
      } else {
        console.error(data.message);
      }
    })
    .catch(function(error) {
      console.error(error);
    });
});
